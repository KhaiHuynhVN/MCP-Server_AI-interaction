import { Project, SyntaxKind, Node, SourceFile, ClassDeclaration, MethodDeclaration, FunctionDeclaration, PropertyDeclaration } from 'ts-morph';
import fg from 'fast-glob';
import * as fs from 'fs';
import * as path from 'path';
import { ScanConfig, ScanOutput, FileInfo, ClassInfo, MethodInfo, PropertyInfo, FunctionInfo, TemplateBinding, TreeNode, DeadCodeItem, InheritanceInfo, CircularDependency, SummaryStats, InterfaceImplementation } from './types.js';

export class ProjectScanner {
  private project: Project;
  private config: ScanConfig;
  private callGraph: Map<string, Set<string>> = new Map();
  private reverseCallGraph: Map<string, Set<string>> = new Map();
  
  private classMethodsMap: Map<string, Set<string>> = new Map();
  private injectionMap: Map<string, Map<string, string>> = new Map();
  private nestedInjectionMap: Map<string, Map<string, string>> = new Map();
  private localInjectionMap: Map<string, Map<string, string>> = new Map();

  constructor(config: ScanConfig) {
    this.config = config;
    this.project = new Project({
      tsConfigFilePath: this.findTsConfig(),
      skipAddingFilesFromTsConfig: true,
    });
  }

  private findTsConfig(): string | undefined {
    const tsConfigPath = path.join(this.config.path, 'tsconfig.json');
    return fs.existsSync(tsConfigPath) ? tsConfigPath : undefined;
  }

  async scan(): Promise<ScanOutput> {
    const startTime = Date.now();

    const patterns = this.config.include || ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx', '**/*.mts', '**/*.mjs'];
    const ignorePatterns = ['**/node_modules/**', '**/*.spec.ts', '**/*.test.ts', '**/dist/**', '**/build/**', ...(this.config.exclude || [])];

    const files = await fg(patterns, { cwd: this.config.path, ignore: ignorePatterns, absolute: true });

    for (const file of files) {
      this.project.addSourceFileAtPath(file);
    }

    // Pass 1: Collect all class methods and DI mappings
    this.collectClassInfo();

    const fileInfos: FileInfo[] = [];
    for (const sourceFile of this.project.getSourceFiles()) {
      const fileInfo = this.scanFile(sourceFile);
      fileInfos.push(fileInfo);

      if (this.config.framework === 'angular') {
        const templateBindings = await this.scanAngularTemplate(sourceFile);
        if (templateBindings.length > 0) {
          fileInfo.templateBindings = templateBindings;
          this.addTemplateBindingsToCallGraph(fileInfo, templateBindings);
        }
      }
    }

    // Pass 2: Resolve cross-file calls
    this.resolveCrossFileCalls(fileInfos);

    this.buildCallGraph(fileInfos);
    const tree = this.buildTree(files);

    const classCount = fileInfos.reduce((sum, f) => sum + f.classes.length, 0);
    const functionCount = fileInfos.reduce((sum, f) => sum + f.functions.length, 0);

    const deadCode = this.detectDeadCode(fileInfos);
    const inheritance = this.analyzeInheritance(fileInfos);
    const circularDependencies = this.detectCircularDependencies(fileInfos);
    const summary = this.generateSummary(fileInfos);
    const interfaceImplementations = this.analyzeInterfaceImplementations(fileInfos);

    this.buildCallChains(fileInfos, 3);

    console.log(`Scan completed in ${Date.now() - startTime}ms`);
    console.log(`Files: ${files.length}, Classes: ${classCount}, Functions: ${functionCount}`);
    console.log(`Dead code: ${deadCode.length}, Inheritance: ${inheritance.length}, Interfaces: ${interfaceImplementations.length}`);

    return {
      meta: { path: this.config.path, framework: this.config.framework, scannedAt: new Date().toISOString(), fileCount: files.length, classCount, functionCount },
      tree,
      files: fileInfos,
      callGraph: this.serializeCallGraph(),
      deadCode,
      inheritance,
      circularDependencies,
      summary,
      interfaceImplementations,
    };
  }

  private collectClassInfo() {
    const classPropertiesMap = new Map<string, Map<string, string>>();

    for (const sourceFile of this.project.getSourceFiles()) {
      for (const cls of sourceFile.getClasses()) {
        const className = cls.getName();
        if (!className) continue;

        // Collect method names
        const methods = new Set<string>();
        cls.getMethods().forEach((m) => methods.add(m.getName()));
        this.classMethodsMap.set(className, methods);

        // Collect all property injections
        const injections = new Map<string, string>();
        
        cls.getProperties().forEach((prop) => {
          const initializer = prop.getInitializer()?.getText() || '';
          const injectMatch = initializer.match(/inject\s*\(\s*(\w+)\s*\)/);
          if (injectMatch) {
            injections.set(prop.getName(), injectMatch[1]);
          }
        });

        // Check constructor parameters
        const constructor = cls.getConstructors()[0];
        if (constructor) {
          constructor.getParameters().forEach((param) => {
            const typeNode = param.getTypeNode();
            if (typeNode) {
              const typeName = typeNode.getText();
              if (typeName.endsWith('Service') || this.classMethodsMap.has(typeName)) {
                injections.set(param.getName(), typeName);
              }
            }
          });
        }

        if (injections.size > 0) {
          this.injectionMap.set(className, injections);
          classPropertiesMap.set(className, injections);
        }
      }
    }

    this.nestedInjectionMap = classPropertiesMap;
  }

  private resolveCrossFileCalls(fileInfos: FileInfo[]) {
    for (const fileInfo of fileInfos) {
      for (const cls of fileInfo.classes) {
        const className = cls.name;
        const injections = this.injectionMap.get(className) || new Map();

        for (const method of cls.methods) {
          const callerFullName = `${className}.${method.name}`;

          for (const call of method.calls) {
            let resolvedCall: string | null = null;

            const simpleMatch = call.match(/^this\.(_?\w+)\s*\.\s*(\w+)/);
            if (simpleMatch) {
              const propName = simpleMatch[1];
              const methodName = simpleMatch[2];
              
              const serviceClass = injections.get(propName);
              if (serviceClass) {
                const nestedProps = this.nestedInjectionMap.get(serviceClass);
                if (nestedProps && nestedProps.has(methodName)) {
                } else {
                  resolvedCall = `${serviceClass}.${methodName}`;
                }
              }
            }

            const nestedMatch = call.match(/^this\.(_?\w+)\s*\.\s*(\w+)\s*\.\s*(\w+)/);
            if (nestedMatch) {
              const propName = nestedMatch[1];
              const nestedProp = nestedMatch[2];
              const methodName = nestedMatch[3];

              const serviceClass = injections.get(propName);
              if (serviceClass) {
                const nestedInjections = this.nestedInjectionMap.get(serviceClass);
                if (nestedInjections) {
                  const nestedServiceClass = nestedInjections.get(nestedProp);
                  if (nestedServiceClass) {
                    resolvedCall = `${nestedServiceClass}.${methodName}`;
                  }
                }
              }
            }

            const injectMatch = call.match(/inject\s*\(\s*(\w+)\s*\)\s*\.\s*(\w+)/);
            if (injectMatch) {
              const serviceClass = injectMatch[1];
              const methodName = injectMatch[2];
              if (this.classMethodsMap.has(serviceClass)) {
                resolvedCall = `${serviceClass}.${methodName}`;
              }
            }

            if (resolvedCall) {
              if (!this.reverseCallGraph.has(resolvedCall)) {
                this.reverseCallGraph.set(resolvedCall, new Set());
              }
              this.reverseCallGraph.get(resolvedCall)!.add(callerFullName);
            }
          }
        }
      }

      for (const fn of fileInfo.functions) {
        const callerFullName = fn.name;
        const localInjections = this.localInjectionMap.get(fn.name) || new Map();

        for (const call of fn.calls) {
          let resolvedCall: string | null = null;

          const injectMatch = call.match(/inject\s*\(\s*(\w+)\s*\)\s*\.\s*(\w+)/);
          if (injectMatch) {
            const serviceClass = injectMatch[1];
            const methodName = injectMatch[2];
            if (this.classMethodsMap.has(serviceClass)) {
              resolvedCall = `${serviceClass}.${methodName}`;
            }
          }

          const localVarMatch = call.match(/^(\w+)\s*\.\s*(\w+)/);
          if (!resolvedCall && localVarMatch) {
            const varName = localVarMatch[1];
            const methodName = localVarMatch[2];
            const serviceClass = localInjections.get(varName);
            if (serviceClass && this.classMethodsMap.has(serviceClass)) {
              resolvedCall = `${serviceClass}.${methodName}`;
            }
          }

          if (resolvedCall) {
            if (!this.reverseCallGraph.has(resolvedCall)) {
              this.reverseCallGraph.set(resolvedCall, new Set());
            }
            this.reverseCallGraph.get(resolvedCall)!.add(`function:${callerFullName}`);
          }
        }
      }
    }
  }

  private scanFile(sourceFile: SourceFile): FileInfo {
    const filePath = sourceFile.getFilePath();
    return {
      path: filePath,
      relativePath: path.relative(this.config.path, filePath).replace(/\\/g, '/'),
      imports: this.getImports(sourceFile),
      exports: this.getExports(sourceFile),
      classes: this.getClasses(sourceFile),
      functions: this.getFunctions(sourceFile),
    };
  }

  private getImports(sourceFile: SourceFile) {
    return sourceFile.getImportDeclarations().map((imp) => ({
      module: imp.getModuleSpecifierValue(),
      named: imp.getNamedImports().map((n) => n.getName()),
    }));
  }

  private getExports(sourceFile: SourceFile): string[] {
    const exports: string[] = [];
    sourceFile.getExportDeclarations().forEach((exp) => exp.getNamedExports().forEach((named) => exports.push(named.getName())));
    sourceFile.getClasses().forEach((cls) => cls.isExported() && exports.push(cls.getName() || 'anonymous'));
    sourceFile.getFunctions().forEach((fn) => fn.isExported() && exports.push(fn.getName() || 'anonymous'));
    return exports;
  }

  private getClasses(sourceFile: SourceFile): ClassInfo[] {
    return sourceFile.getClasses().map((cls) => this.scanClass(cls));
  }

  private scanClass(cls: ClassDeclaration): ClassInfo {
    const className = cls.getName() || 'anonymous';
    return {
      name: className,
      line: cls.getStartLineNumber(),
      extends: cls.getExtends()?.getText(),
      implements: cls.getImplements().map((i) => i.getText()),
      decorators: cls.getDecorators().map((d) => `@${d.getName()}`),
      methods: cls.getMethods().map((m) => this.scanMethod(m, className)),
      properties: cls.getProperties().map((p) => this.scanProperty(p)),
    };
  }

  private scanMethod(method: MethodDeclaration, className: string): MethodInfo {
    const methodName = method.getName();
    const fullName = `${className}.${methodName}`;
    const calls = this.extractCalls(method);

    this.callGraph.set(fullName, new Set(calls));
    calls.forEach((call) => {
      if (!this.reverseCallGraph.has(call)) this.reverseCallGraph.set(call, new Set());
      this.reverseCallGraph.get(call)!.add(fullName);
    });

    return {
      name: methodName,
      line: method.getStartLineNumber(),
      params: method.getParameters().map((p) => ({ name: p.getName(), type: this.cleanType(p.getType().getText()) })),
      returnType: this.cleanType(method.getReturnType().getText()),
      modifiers: method.getModifiers().map((m) => m.getText()),
      decorators: method.getDecorators().map((d) => `@${d.getName()}`),
      calls,
      calledBy: [],
    };
  }

  private cleanType(typeStr: string): string {
    // Keep original type from TypeScript compiler - no transformation
    return typeStr || 'any';
  }

  private scanProperty(prop: PropertyDeclaration): PropertyInfo {
    return {
      name: prop.getName(),
      line: prop.getStartLineNumber(),
      type: this.cleanType(prop.getType().getText()),
      modifiers: prop.getModifiers().map((m) => m.getText()),
      decorators: prop.getDecorators().map((d) => `@${d.getName()}`),
      initializer: prop.getInitializer()?.getText()?.substring(0, 100),
    };
  }

  private getFunctions(sourceFile: SourceFile): FunctionInfo[] {
    const functions: FunctionInfo[] = [];
    
    sourceFile.getFunctions().forEach((fn) => {
      functions.push(this.scanFunction(fn));
    });

    sourceFile.getVariableDeclarations().forEach((varDecl) => {
      const initializer = varDecl.getInitializer();
      if (!initializer) return;

      const kind = initializer.getKind();
      if (kind === SyntaxKind.ArrowFunction || kind === SyntaxKind.FunctionExpression) {
        const fnName = varDecl.getName();
        const calls = this.extractCalls(initializer);
        this.callGraph.set(fnName, new Set(calls));

        const localInjections = this.extractLocalInjections(initializer);
        if (localInjections.size > 0) {
          this.localInjectionMap.set(fnName, localInjections);
        }

        const varStatement = varDecl.getFirstAncestorByKind(SyntaxKind.VariableStatement);
        const isExported = varStatement?.isExported() ?? false;

        let params: { name: string; type: string }[] = [];
        let returnType = 'any';

        if (kind === SyntaxKind.ArrowFunction) {
          const arrowFn = initializer.asKind(SyntaxKind.ArrowFunction);
          if (arrowFn) {
            params = arrowFn.getParameters().map((p) => ({ name: p.getName(), type: this.cleanType(p.getType().getText()) }));
            returnType = this.cleanType(arrowFn.getReturnType().getText());
          }
        } else if (kind === SyntaxKind.FunctionExpression) {
          const fnExpr = initializer.asKind(SyntaxKind.FunctionExpression);
          if (fnExpr) {
            params = fnExpr.getParameters().map((p) => ({ name: p.getName(), type: this.cleanType(p.getType().getText()) }));
            returnType = this.cleanType(fnExpr.getReturnType().getText());
          }
        }

        functions.push({
          name: fnName,
          line: varDecl.getStartLineNumber(),
          params,
          returnType,
          calls,
          exported: isExported,
        });
      }
    });

    return functions;
  }

  private scanFunction(fn: FunctionDeclaration): FunctionInfo {
    const fnName = fn.getName() || 'anonymous';
    const calls = this.extractCalls(fn);
    this.callGraph.set(fnName, new Set(calls));

    const localInjections = this.extractLocalInjections(fn);
    if (localInjections.size > 0) {
      this.localInjectionMap.set(fnName, localInjections);
    }

    return {
      name: fnName,
      line: fn.getStartLineNumber(),
      params: fn.getParameters().map((p) => ({ name: p.getName(), type: this.cleanType(p.getType().getText()) })),
      returnType: this.cleanType(fn.getReturnType().getText()),
      calls,
      exported: fn.isExported(),
    };
  }

  private extractCalls(node: Node): string[] {
    const calls: string[] = [];
    node.forEachDescendant((descendant) => {
      if (descendant.getKind() === SyntaxKind.CallExpression) {
        const callExpr = descendant.asKind(SyntaxKind.CallExpression);
        if (callExpr) {
          let callName = callExpr.getExpression().getText();
          callName = callName.replace(/\s+/g, ' ').trim();
          if (callName) calls.push(callName);
        }
      }
    });
    return [...new Set(calls)];
  }

  private extractLocalInjections(node: Node): Map<string, string> {
    const localMap = new Map<string, string>();
    node.forEachDescendant((descendant) => {
      if (descendant.getKind() === SyntaxKind.VariableDeclaration) {
        const varDecl = descendant.asKind(SyntaxKind.VariableDeclaration);
        if (varDecl) {
          const initText = varDecl.getInitializer()?.getText() || '';
          const match = initText.match(/^inject\s*\(\s*(\w+)\s*\)/);
          if (match) {
            localMap.set(varDecl.getName(), match[1]);
          }
        }
      }
    });
    return localMap;
  }

  private async scanAngularTemplate(sourceFile: SourceFile): Promise<TemplateBinding[]> {
    const bindings: TemplateBinding[] = [];
    const filePath = sourceFile.getFilePath();

    for (const cls of sourceFile.getClasses()) {
      const componentDecorator = cls.getDecorator('Component');
      if (!componentDecorator) continue;

      const args = componentDecorator.getArguments()[0];
      if (!args) continue;
      const argsText = args.getText();

      const templateUrlMatch = argsText.match(/templateUrl:\s*['"]([^'"]+)['"]/);
      if (templateUrlMatch) {
        const templatePath = path.resolve(path.dirname(filePath), templateUrlMatch[1]);
        if (fs.existsSync(templatePath)) {
          bindings.push(...this.parseAngularTemplate(fs.readFileSync(templatePath, 'utf-8')));
        }
      }

      const templateMatch = argsText.match(/template:\s*`([^`]*)`/s);
      if (templateMatch) {
        bindings.push(...this.parseAngularTemplate(templateMatch[1]));
      }
    }
    return bindings;
  }

  private parseAngularTemplate(template: string): TemplateBinding[] {
    const bindings: TemplateBinding[] = [];
    let match;

    const eventRegex = /\(([^)]+)\)="([^"]+)"/g;
    while ((match = eventRegex.exec(template)) !== null) {
      bindings.push({ type: 'event', expression: match[2] });
    }

    const propRegex = /\[([^\]]+)\]="([^"]+)"/g;
    while ((match = propRegex.exec(template)) !== null) {
      bindings.push({ type: 'property', expression: match[2] });
    }

    const interpRegex = /\{\{\s*([^}]+)\s*\}\}/g;
    while ((match = interpRegex.exec(template)) !== null) {
      bindings.push({ type: 'interpolation', expression: match[1].trim() });
    }

    const structuralRegex = /(\*ngIf|\*ngFor|@if|@for|@switch)(?:="([^"]+)"|\s*\(([^)]+)\))/g;
    while ((match = structuralRegex.exec(template)) !== null) {
      bindings.push({ type: 'structural', expression: match[2] || match[3] || '' });
    }

    return bindings;
  }

  private addTemplateBindingsToCallGraph(fileInfo: FileInfo, bindings: TemplateBinding[]) {
    const className = fileInfo.classes[0]?.name;
    if (!className) return;

    bindings.forEach((binding) => {
      const methodMatch = binding.expression.match(/(\w+)\s*\(/);
      if (methodMatch) {
        const fullName = `${className}.${methodMatch[1]}`;
        if (!this.reverseCallGraph.has(fullName)) this.reverseCallGraph.set(fullName, new Set());
        this.reverseCallGraph.get(fullName)!.add(`template:${fileInfo.relativePath}`);
      }
    });
  }

  private buildCallGraph(fileInfos: FileInfo[]) {
    fileInfos.forEach((file) => {
      file.classes.forEach((cls) => {
        cls.methods.forEach((method) => {
          const callers = this.reverseCallGraph.get(`${cls.name}.${method.name}`);
          if (callers) method.calledBy = [...callers];
        });
      });
    });
  }

  private serializeCallGraph(): Record<string, string[]> {
    const result: Record<string, string[]> = {};
    this.callGraph.forEach((calls, caller) => (result[caller] = [...calls]));
    return result;
  }

  private buildTree(files: string[]): TreeNode {
    const root: TreeNode = { name: path.basename(this.config.path), type: 'directory', children: [] };

    const addToTree = (parts: string[], current: TreeNode) => {
      if (parts.length === 0) return;
      const [first, ...rest] = parts;
      let child = current.children?.find((c) => c.name === first);
      if (!child) {
        child = { name: first, type: rest.length === 0 ? 'file' : 'directory', children: rest.length === 0 ? undefined : [] };
        current.children?.push(child);
      }
      if (rest.length > 0 && child.children) addToTree(rest, child);
    };

    files.forEach((file) => {
      const relativePath = path.relative(this.config.path, file);
      addToTree(relativePath.split(path.sep), root);
    });

    return root;
  }

  private detectDeadCode(fileInfos: FileInfo[]): DeadCodeItem[] {
    const deadCode: DeadCodeItem[] = [];
    const lifecycleHooks = new Set([
      'ngOnInit', 'ngOnDestroy', 'ngOnChanges', 'ngDoCheck',
      'ngAfterContentInit', 'ngAfterContentChecked',
      'ngAfterViewInit', 'ngAfterViewChecked',
      'constructor', 'canActivate', 'canDeactivate', 'resolve'
    ]);

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        for (const method of cls.methods) {
          if (method.calledBy.length === 0) {
            if (lifecycleHooks.has(method.name)) continue;
            if (method.name.startsWith('_') && method.modifiers.includes('private')) continue;

            deadCode.push({
              type: 'method',
              name: method.name,
              fullName: `${cls.name}.${method.name}`,
              file: file.relativePath,
              line: method.line,
              reason: 'No callers found'
            });
          }
        }
      }

      for (const fn of file.functions) {
        const callers = this.reverseCallGraph.get(fn.name);
        if (!callers || callers.size === 0) {
          if (fn.exported) continue;

          deadCode.push({
            type: 'function',
            name: fn.name,
            fullName: fn.name,
            file: file.relativePath,
            line: fn.line,
            reason: 'No callers found and not exported'
          });
        }
      }
    }

    return deadCode;
  }

  private analyzeInheritance(fileInfos: FileInfo[]): InheritanceInfo[] {
    const inheritance: InheritanceInfo[] = [];
    const classMethodsCache = new Map<string, Set<string>>();
    const classExtendsCache = new Map<string, string | undefined>();

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        classMethodsCache.set(cls.name, new Set(cls.methods.map(m => m.name)));
        classExtendsCache.set(cls.name, cls.extends);
      }
    }

    const getAllAncestorMethods = (className: string, visited = new Set<string>()): Set<string> => {
      const allMethods = new Set<string>();
      const parentName = classExtendsCache.get(className);
      
      if (!parentName || visited.has(parentName)) return allMethods;
      visited.add(parentName);
      
      const parentMethods = classMethodsCache.get(parentName);
      if (parentMethods) {
        parentMethods.forEach(m => allMethods.add(m));
      }
      
      const grandparentMethods = getAllAncestorMethods(parentName, visited);
      grandparentMethods.forEach(m => allMethods.add(m));
      
      return allMethods;
    };

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        if (cls.extends) {
          const allAncestorMethods = getAllAncestorMethods(cls.name);
          if (allAncestorMethods.size > 0) {
            const childMethods = new Set(cls.methods.map(m => m.name));
            const inheritedMethods: string[] = [];
            const overriddenMethods: string[] = [];

            allAncestorMethods.forEach(method => {
              if (childMethods.has(method)) {
                overriddenMethods.push(method);
              } else {
                inheritedMethods.push(method);
              }
            });

            inheritance.push({
              className: cls.name,
              extends: cls.extends,
              inheritedMethods,
              overriddenMethods
            });
          }
        }
      }
    }

    return inheritance;
  }

  private detectCircularDependencies(fileInfos: FileInfo[]): CircularDependency[] {
    const cycles: CircularDependency[] = [];
    const importGraph = new Map<string, Set<string>>();

    for (const file of fileInfos) {
      const deps = new Set<string>();
      for (const imp of file.imports) {
        if (imp.module.startsWith('.')) {
          const resolved = this.resolveImportPath(file.relativePath, imp.module);
          if (resolved) deps.add(resolved);
        }
      }
      importGraph.set(file.relativePath, deps);
    }

    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const dfs = (node: string, path: string[]): void => {
      visited.add(node);
      recursionStack.add(node);

      const deps = importGraph.get(node);
      if (deps) {
        for (const dep of deps) {
          if (!visited.has(dep)) {
            dfs(dep, [...path, dep]);
          } else if (recursionStack.has(dep)) {
            const cycleStart = path.indexOf(dep);
            const cycle = cycleStart >= 0 ? path.slice(cycleStart) : [...path, dep];
            cycle.push(dep);
            
            const cycleKey = [...cycle].sort().join('->');
            if (!cycles.some(c => [...c.cycle].sort().join('->') === cycleKey)) {
              cycles.push({
                cycle,
                description: `Circular: ${cycle.join(' -> ')}`
              });
            }
          }
        }
      }

      recursionStack.delete(node);
    };

    for (const file of importGraph.keys()) {
      if (!visited.has(file)) {
        dfs(file, [file]);
      }
    }

    return cycles;
  }

  private resolveImportPath(fromFile: string, importPath: string): string | null {
    const fromDir = fromFile.substring(0, fromFile.lastIndexOf('/'));
    const parts = importPath.split('/');
    let currentPath = fromDir;

    for (const part of parts) {
      if (part === '.') continue;
      if (part === '..') {
        currentPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
      } else {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
      }
    }

    const extensions = ['.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.js'];
    for (const ext of extensions) {
      const fullPath = currentPath + ext;
      if (this.project.getSourceFile(f => f.getFilePath().replace(/\\/g, '/').endsWith(fullPath))) {
        return currentPath + (ext.startsWith('/') ? ext : ext.replace('.ts', '.ts').replace('.js', '.ts'));
      }
    }

    return currentPath.endsWith('.ts') || currentPath.endsWith('.js') ? currentPath : null;
  }

  private generateSummary(fileInfos: FileInfo[]): SummaryStats {
    const methodCallCounts = new Map<string, number>();
    const serviceUsageCounts = new Map<string, number>();
    
    for (const file of fileInfos) {
      for (const cls of file.classes) {
        for (const method of cls.methods) {
          const fullName = `${cls.name}.${method.name}`;
          methodCallCounts.set(fullName, method.calledBy.length);
        }
        
        if (cls.decorators.some(d => d.includes('Injectable') || d.includes('Service'))) {
          serviceUsageCounts.set(cls.name, 0);
        }
      }
    }

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        for (const method of cls.methods) {
          for (const call of method.calls) {
            const serviceMatch = call.match(/this\.(_?\w+)\./);
            if (serviceMatch) {
              const propName = serviceMatch[1];
              const injections = this.injectionMap.get(cls.name);
              if (injections) {
                const serviceName = injections.get(propName);
                if (serviceName && serviceUsageCounts.has(serviceName)) {
                  serviceUsageCounts.set(serviceName, (serviceUsageCounts.get(serviceName) || 0) + 1);
                }
              }
            }
          }
        }
      }
    }

    const mostCalledMethods = [...methodCallCounts.entries()]
      .filter(([_, count]) => count > 0)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, callerCount]) => ({ name, callerCount }));

    const mostUsedServices = [...serviceUsageCounts.entries()]
      .filter(([_, count]) => count > 0)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name, usageCount]) => ({ name, usageCount }));

    const largestClasses = fileInfos
      .flatMap(f => f.classes.map(c => ({ name: c.name, methodCount: c.methods.length, file: f.relativePath })))
      .sort((a, b) => b.methodCount - a.methodCount)
      .slice(0, 10);

    const filesByImports = fileInfos
      .map(f => ({ file: f.relativePath, importCount: f.imports.length }))
      .sort((a, b) => b.importCount - a.importCount)
      .slice(0, 10);

    return {
      mostCalledMethods,
      mostUsedServices,
      largestClasses,
      filesByImports
    };
  }

  private buildCallChains(fileInfos: FileInfo[], maxDepth: number): void {
    const reverseGraph = new Map<string, Set<string>>();
    
    for (const [caller, calls] of this.callGraph) {
      for (const call of calls) {
        if (!reverseGraph.has(call)) {
          reverseGraph.set(call, new Set());
        }
        reverseGraph.get(call)!.add(caller);
      }
    }

    const getCallChain = (methodName: string, depth: number, visited: Set<string>): string[][] => {
      if (depth <= 0 || visited.has(methodName)) return [];
      visited.add(methodName);

      const chains: string[][] = [];
      const callers = this.reverseCallGraph.get(methodName);
      
      if (!callers || callers.size === 0) {
        return [[methodName]];
      }

      for (const caller of callers) {
        if (caller.startsWith('template:')) {
          chains.push([caller, methodName]);
        } else {
          const parentChains = getCallChain(caller, depth - 1, new Set(visited));
          if (parentChains.length === 0) {
            chains.push([caller, methodName]);
          } else {
            for (const chain of parentChains) {
              chains.push([...chain, methodName]);
            }
          }
        }
      }

      return chains;
    };

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        for (const method of cls.methods) {
          const fullName = `${cls.name}.${method.name}`;
          if (method.calledBy.length > 0) {
            const chains = getCallChain(fullName, maxDepth, new Set());
            if (chains.length > 0 && chains.some(c => c.length > 1)) {
              method.callChain = chains.filter(c => c.length > 1).slice(0, 5);
            }
          }
        }
      }
    }
  }

  private analyzeInterfaceImplementations(fileInfos: FileInfo[]): InterfaceImplementation[] {
    const interfaceMap = new Map<string, Set<string>>();

    for (const file of fileInfos) {
      for (const cls of file.classes) {
        for (const iface of cls.implements) {
          const cleanName = iface.replace(/<.*>/, '').trim();
          if (!interfaceMap.has(cleanName)) {
            interfaceMap.set(cleanName, new Set());
          }
          interfaceMap.get(cleanName)!.add(cls.name);
        }
      }
    }

    return [...interfaceMap.entries()]
      .map(([interfaceName, implementors]) => ({
        interfaceName,
        implementedBy: [...implementors]
      }))
      .sort((a, b) => b.implementedBy.length - a.implementedBy.length);
  }
}

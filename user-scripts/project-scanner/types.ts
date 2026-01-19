export interface ScanConfig {
  path: string;
  framework: 'angular' | 'react' | 'generic';
  depth?: number;
  include?: string[];
  exclude?: string[];
  query?: string;
}

export interface MethodInfo {
  name: string;
  line: number;
  params: { name: string; type: string }[];
  returnType: string;
  modifiers: string[];
  decorators: string[];
  calls: string[];
  calledBy: string[];
  callChain?: string[][];
}

export interface PropertyInfo {
  name: string;
  line: number;
  type: string;
  modifiers: string[];
  decorators: string[];
  initializer?: string;
}

export interface ClassInfo {
  name: string;
  line: number;
  extends?: string;
  implements: string[];
  decorators: string[];
  methods: MethodInfo[];
  properties: PropertyInfo[];
}

export interface FunctionInfo {
  name: string;
  line: number;
  params: { name: string; type: string }[];
  returnType: string;
  calls: string[];
  exported: boolean;
}

export interface TemplateBinding {
  type: 'event' | 'property' | 'interpolation' | 'structural';
  expression: string;
  line?: number;
}

export interface FileInfo {
  path: string;
  relativePath: string;
  imports: { module: string; named: string[] }[];
  exports: string[];
  classes: ClassInfo[];
  functions: FunctionInfo[];
  templateBindings?: TemplateBinding[];
}

export interface TreeNode {
  name: string;
  type: 'file' | 'directory';
  children?: TreeNode[];
}

export interface DeadCodeItem {
  type: 'method' | 'function';
  name: string;
  fullName: string;
  file: string;
  line: number;
  reason: string;
}

export interface InheritanceInfo {
  className: string;
  extends: string;
  inheritedMethods: string[];
  overriddenMethods: string[];
}

export interface CircularDependency {
  cycle: string[];
  description: string;
}

export interface SummaryStats {
  mostCalledMethods: { name: string; callerCount: number }[];
  mostUsedServices: { name: string; usageCount: number }[];
  largestClasses: { name: string; methodCount: number; file: string }[];
  filesByImports: { file: string; importCount: number }[];
}

export interface InterfaceImplementation {
  interfaceName: string;
  implementedBy: string[];
}

export interface ScanOutput {
  meta: {
    path: string;
    framework: string;
    scannedAt: string;
    fileCount: number;
    classCount: number;
    functionCount: number;
  };
  tree: TreeNode;
  files: FileInfo[];
  callGraph: Record<string, string[]>;
  deadCode?: DeadCodeItem[];
  inheritance?: InheritanceInfo[];
  circularDependencies?: CircularDependency[];
  summary?: SummaryStats;
  interfaceImplementations?: InterfaceImplementation[];
}

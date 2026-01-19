import { ScanOutput, TreeNode } from './types.js';

export function filterOutput(output: ScanOutput, query: string): ScanOutput {
  const queryLower = query.toLowerCase();

  // Filter files
  const filteredFiles = output.files.filter((file) => {
    if (file.relativePath.toLowerCase().includes(queryLower)) return true;
    if (file.classes.some((cls) => cls.name.toLowerCase().includes(queryLower))) return true;
    const dirParts = query.replace(/\\/g, '/').split('/');
    if (dirParts.every((part) => file.relativePath.toLowerCase().includes(part.toLowerCase()))) return true;
    return false;
  });

  // Filter call graph
  const relevantMethods = new Set<string>();
  filteredFiles.forEach((file) => {
    file.classes.forEach((cls) => {
      cls.methods.forEach((method) => relevantMethods.add(`${cls.name}.${method.name}`));
    });
    file.functions.forEach((fn) => relevantMethods.add(fn.name));
  });

  const filteredCallGraph: Record<string, string[]> = {};
  Object.entries(output.callGraph).forEach(([key, value]) => {
    if (relevantMethods.has(key) || key.toLowerCase().includes(queryLower)) {
      filteredCallGraph[key] = value;
    }
  });

  // Build filtered tree from filtered file paths
  const filteredPaths = filteredFiles.map((f) => f.relativePath);
  const filteredTree = buildTreeFromPaths(filteredPaths);

  return {
    meta: {
      ...output.meta,
      fileCount: filteredFiles.length,
      classCount: filteredFiles.reduce((sum, f) => sum + f.classes.length, 0),
      functionCount: filteredFiles.reduce((sum, f) => sum + f.functions.length, 0),
    },
    tree: filteredTree,
    files: filteredFiles,
    callGraph: filteredCallGraph,
  };
}

function buildTreeFromPaths(paths: string[]): TreeNode {
  const root: TreeNode = {
    name: 'filtered',
    type: 'directory',
    children: [],
  };

  for (const filePath of paths) {
    const parts = filePath.replace(/\\/g, '/').split('/');
    let current = root;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isFile = i === parts.length - 1;

      if (!current.children) current.children = [];

      let child = current.children.find((c) => c.name === part);
      if (!child) {
        child = {
          name: part,
          type: isFile ? 'file' : 'directory',
          children: isFile ? undefined : [],
        };
        current.children.push(child);
      }
      current = child;
    }
  }

  // Clean up empty children arrays
  const cleanup = (node: TreeNode) => {
    if (node.children?.length === 0) {
      delete node.children;
    } else {
      node.children?.forEach(cleanup);
    }
  };
  cleanup(root);

  return root;
}

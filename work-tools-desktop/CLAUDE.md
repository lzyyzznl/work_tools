# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a desktop application for batch file processing built with Electron, Vue 3, and TypeScript. The application has two main features:

1. **File Matcher**: Match files based on custom rules
2. **File Renamer**: Batch rename files with various operations (replace, add, delete, number, etc.)

## Architecture

- **Frontend**: Vue 3 with Composition API and TypeScript
- **Desktop Framework**: Electron with Electron Forge
- **State Management**: Pinia
- **Build Tool**: Vite
- **Styling**: UnoCSS (Atomic CSS)
- **UI Components**: vxe-table for data tables
- **Testing**: Vitest with jsdom environment

## Project Structure

```
work-tools-desktop/
├── src/
│   ├── main/           # Electron main process
│   │   ├── main.ts     # Main process entry point
│   │   ├── preload.ts  # Preload script for secure IPC
│   │   └── fileSystem.ts # File system operations
│   └── renderer/       # Vue 3 frontend application
│       ├── App.vue     # Root component
│       ├── components/ # Vue components
│       │   ├── common/      # Shared components
│       │   ├── file-matcher/ # File matcher components
│       │   └── file-renamer/ # File renamer components
│       ├── composables/     # Reusable composition functions
│       ├── stores/          # Pinia stores for state management
│       ├── types/           # TypeScript type definitions
│       └── constants/       # Application constants
├── assets/             # Static assets
├── docs/               # Documentation
└── tests/              # Test files
```

## Common Commands

### Development

```bash
# Install dependencies (using pnpm)
pnpm install

# Start development server with hot reload
pnpm start
```

### Testing

```bash
# Run all tests
pnpm test:run

# Interactive test mode
pnpm test

# Test UI
pnpm test:ui

# Run specific test file
pnpm test -- tests/components/FileTable.test.ts
```

### Linting

```bash
# Lint code
pnpm lint
```

### Building

```bash
# Package the application
pnpm package

# Create installer
pnpm make
```

## Key Files

- `src/main/main.ts`: Electron main process entry point
- `src/renderer/App.vue`: Main Vue application component
- `src/renderer/renderer.ts`: Vue application initialization
- `src/renderer/stores/*`: Pinia state management stores
- `src/renderer/components/file-matcher/*`: File matcher UI components
- `src/renderer/components/file-renamer/*`: File renamer UI components
- `forge.config.ts`: Electron Forge configuration
- `vitest.config.ts`: Test configuration
- `uno.config.ts`: UnoCSS styling configuration
- `vite.main.config.ts`: Vite main process configuration
- `vite.renderer.config.ts`: Vite renderer process configuration
- `vite.preload.config.ts`: Vite preload script configuration

## Development Guidelines

1. Use TypeScript for type safety
2. Follow Vue 3 Composition API patterns
3. Use UnoCSS atomic classes for styling
4. Maintain component single responsibility principle
5. Use Pinia for state management
6. Write tests for new functionality
7. Follow commit message conventions (feat, fix, docs, etc.)

## Path Aliases

The project uses the following path aliases in `vite.renderer.config.ts`:
- `@`: `src` - Root source directory
- `@/types`: `src/renderer/types` - TypeScript type definitions
- `@/components`: `src/renderer/components` - Vue components
- `@/composables`: `src/renderer/composables` - Composition functions
- `@/stores`: `src/renderer/stores` - Pinia stores
- `@/utils`: `src/renderer/utils` - Utility functions

## Build Configuration

The project uses multiple Vite configurations for different Electron processes:
- **Main Process**: `vite.main.config.ts` - Electron main process
- **Renderer Process**: `vite.renderer.config.ts` - Vue frontend with UnoCSS
- **Preload Script**: `vite.preload.config.ts` - Security preload script

## Security Features

The Electron app is configured with security fuses in `forge.config.ts`:
- RunAsNode: false
- EnableCookieEncryption: true
- EnableNodeOptionsEnvironmentVariable: false
- EnableNodeCliInspectArguments: false
- EnableEmbeddedAsarIntegrityValidation: true
- OnlyLoadAppFromAsar: true

# 必须要遵守的约束

1. 不允许自己启动测试程序和启动程序，只要完成功能即可，测试功能由用户自己来完成
2. 规划 todolist 的时候不需要规划测试相关的任务
3. 使用 pnpm 管理包，禁止使用原生的 npm

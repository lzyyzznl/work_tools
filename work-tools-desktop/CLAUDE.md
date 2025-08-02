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
# Start development server with hot reload
npm start

# Install dependencies
npm install
```

### Testing
```bash
# Run all tests
npm run test:run

# Interactive test mode
npm test

# Test UI
npm run test:ui

# Run specific test file
npm test -- tests/components/FileTable.test.ts
```

### Linting
```bash
# Lint code
npm run lint
```

### Building
```bash
# Package the application
npm run package

# Create installer
npm run make
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

## Development Guidelines

1. Use TypeScript for type safety
2. Follow Vue 3 Composition API patterns
3. Use UnoCSS atomic classes for styling
4. Maintain component single responsibility principle
5. Use Pinia for state management
6. Write tests for new functionality
7. Follow commit message conventions (feat, fix, docs, etc.)
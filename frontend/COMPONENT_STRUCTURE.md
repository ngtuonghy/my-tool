# Frontend Component Structure

## Overview
The frontend has been refactored into a modular, production-ready structure following best practices.

## Component Hierarchy

```
src/
├── routes/
│   └── +page.svelte              # Main page (orchestrator)
│
├── lib/
│   ├── components/
│   │   ├── ui/                   # shadcn-svelte components
│   │   ├── FileUploadZone.svelte # File upload with drag-drop
│   │   ├── SheetSelector.svelte  # Multi-sheet selection UI
│   │   ├── SingleSheetResult.svelte # Single sheet results
│   │   └── ProcessResults.svelte # Multi-sheet results
│   │
│   ├── stores/
│   │   └── excelTool.ts          # State management (optional)
│   │
│   └── api.ts                    # API client
```

## Components

### 1. FileUploadZone.svelte
**Purpose**: Handle file upload with drag-and-drop

**Props**:
- `selectedFile: File | null` - Currently selected file
- `onFileSelect: (file: File) => void` - Callback when file is selected

**Features**:
- Drag-and-drop support
- Click to browse
- File size display
- Keyboard accessible

### 2. SheetSelector.svelte
**Purpose**: Multi-sheet selection interface

**Props**:
- `sheets: string[]` - List of sheet names
- `selectedSheets: string[]` - Currently selected sheets
- `isProcessing: boolean` - Processing state
- `onToggleSheet: (sheet: string) => void` - Toggle sheet selection
- `onDownloadAll: () => void` - Download all as ZIP
- `onDownloadSelected: () => void` - Download selected sheets

**Features**:
- Checkbox list for sheet selection
- Download all as ZIP button
- Download selected button
- Sheet count badge

### 3. SingleSheetResult.svelte
**Purpose**: Display results for single-sheet processing

**Props**:
- `uploadResponse: UploadResponse` - Upload response data
- `onDownload: (filename: string) => void` - Download callback

**Features**:
- Statistics grid (rows, columns, cleaned, renamed)
- Download button
- Success indicator

### 4. ProcessResults.svelte
**Purpose**: Display results for multiple processed sheets

**Props**:
- `results: SheetResult[]` - Array of sheet results
- `onDownload: (filename: string) => void` - Download callback
- `onReset: () => void` - Reset form callback

**Features**:
- Per-sheet results with stats
- Error handling per sheet
- Individual download buttons
- Reset button

## Main Page (+page.svelte)

**Responsibilities**:
- Orchestrate component interactions
- Handle API calls
- Manage application state
- Handle errors

**State Management**:
- Local state using Svelte reactivity
- Optional: Can be migrated to use `excelTool.ts` store for more complex state

## Benefits of This Structure

✅ **Separation of Concerns**: Each component has a single responsibility
✅ **Reusability**: Components can be reused in other pages
✅ **Testability**: Easier to test individual components
✅ **Maintainability**: Changes are isolated to specific components
✅ **Readability**: Main page is now ~250 lines instead of ~400
✅ **Type Safety**: TypeScript props ensure correct usage

## Future Enhancements

- Add unit tests for each component
- Implement Svelte store for global state (already created in `stores/excelTool.ts`)
- Add loading skeletons
- Add animations/transitions
- Add error boundaries

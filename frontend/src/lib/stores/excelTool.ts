/**
 * Excel Tool State Management
 * Handles all state logic for the Excel processing workflow
 */

import { writable, derived } from 'svelte/store';
import type { UploadResponse, SheetResult } from '$lib/api';

export interface ExcelToolState {
	selectedFile: File | null;
	skipRows: number;
	isUploading: boolean;
	uploadResponse: UploadResponse | null;
	selectedSheets: string[];
	isProcessing: boolean;
	processResults: SheetResult[];
	errorMessage: string;
}

function createExcelToolStore() {
	const initialState: ExcelToolState = {
		selectedFile: null,
		skipRows: 8,
		isUploading: false,
		uploadResponse: null,
		selectedSheets: [],
		isProcessing: false,
		processResults: [],
		errorMessage: ''
	};

	const { subscribe, set, update } = writable<ExcelToolState>(initialState);

	return {
		subscribe,
		setFile: (file: File | null) => update(state => ({ ...state, selectedFile: file, uploadResponse: null, processResults: [], errorMessage: '' })),
		setSkipRows: (rows: number) => update(state => ({ ...state, skipRows: rows })),
		setUploading: (uploading: boolean) => update(state => ({ ...state, isUploading: uploading })),
		setUploadResponse: (response: UploadResponse | null) => update(state => ({ ...state, uploadResponse: response })),
		setSelectedSheets: (sheets: string[]) => update(state => ({ ...state, selectedSheets: sheets })),
		toggleSheet: (sheet: string) => update(state => ({
			...state,
			selectedSheets: state.selectedSheets.includes(sheet)
				? state.selectedSheets.filter(s => s !== sheet)
				: [...state.selectedSheets, sheet]
		})),
		setProcessing: (processing: boolean) => update(state => ({ ...state, isProcessing: processing })),
		setProcessResults: (results: SheetResult[]) => update(state => ({ ...state, processResults: results })),
		setError: (error: string) => update(state => ({ ...state, errorMessage: error })),
		reset: () => set(initialState)
	};
}

export const excelToolStore = createExcelToolStore();

// Derived stores for convenience
export const hasFile = derived(excelToolStore, $state => $state.selectedFile !== null);
export const hasSingleSheetResult = derived(excelToolStore, $state => 
	$state.uploadResponse?.single_sheet === true && $state.uploadResponse.stats !== undefined
);
export const hasMultipleSheets = derived(excelToolStore, $state => 
	$state.uploadResponse?.multiple_sheets === true && $state.uploadResponse.sheets !== undefined
);
export const hasProcessResults = derived(excelToolStore, $state => $state.processResults.length > 0);

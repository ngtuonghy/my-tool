/**
 * API Client for Excel Tool Backend
 */

import { env } from '$env/dynamic/public';

const API_BASE = env.PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// Debug: Log API base URL
console.log('API_BASE:', API_BASE);
console.log('env.PUBLIC_API_BASE_URL:', env.PUBLIC_API_BASE_URL);

export interface UploadResponse {
	success: boolean;
	single_sheet?: boolean;
	multiple_sheets?: boolean;
	sheets?: string[];
	temp_file?: string;
	skip_rows?: number;
	original_filename?: string;
	filename?: string;
	download_url?: string;
	stats?: {
		original_rows: number;
		original_columns: number;
		final_columns: number;
		empty_columns_removed: number;
		unnamed_columns_renamed: number;
	};
	error?: string;
}

export interface ProcessSheetsRequest {
	temp_file: string;
	selected_sheets: string[];
	skip_rows: number;
	original_filename: string;
}

export interface SheetResult {
	sheet_name: string;
	filename?: string;
	download_url?: string;
	stats?: {
		original_rows: number;
		original_columns: number;
		final_columns: number;
		empty_columns_removed: number;
		unnamed_columns_renamed: number;
	};
	error?: string;
}

export interface ProcessSheetsResponse {
	success: boolean;
	results: SheetResult[];
	error?: string;
}

export interface DownloadZipRequest {
	temp_file: string;
	selected_sheets?: string[];
	skip_rows: number;
	original_filename: string;
}

export interface DownloadZipResponse {
	success: boolean;
	filename?: string;
	download_url?: string;
	sheets_processed?: number;
	error?: string;
}

export async function uploadFile(file: File, skipRows: number): Promise<UploadResponse> {
	const formData = new FormData();
	formData.append('file', file);
	formData.append('skip_rows', skipRows.toString());

	const response = await fetch(`${API_BASE}/upload`, {
		method: 'POST',
		body: formData
	});

	return response.json();
}

export async function processSheets(data: ProcessSheetsRequest): Promise<ProcessSheetsResponse> {
	const response = await fetch(`${API_BASE}/process-sheets`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	return response.json();
}

export async function downloadZip(data: DownloadZipRequest): Promise<DownloadZipResponse> {
	const response = await fetch(`${API_BASE}/download-zip`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	return response.json();
}

export function getDownloadUrl(filename: string): string {
	return `${API_BASE}/download/${filename}`;
}

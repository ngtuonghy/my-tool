<script lang="ts">
	import { uploadFile, processSheets, downloadZip, getDownloadUrl } from '$lib/api';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { FileSpreadsheet, Upload, Loader2, AlertCircle } from 'lucide-svelte';
	
	// Custom components
	import FileUploadZone from '$lib/components/FileUploadZone.svelte';
	import SheetSelector from '$lib/components/SheetSelector.svelte';
	import SingleSheetResult from '$lib/components/SingleSheetResult.svelte';
	import ProcessResults from '$lib/components/ProcessResults.svelte';

	let selectedFile: File | null = null;
	let skipRows = 8;
	let isUploading = false;
	let uploadResponse: any = null;
	let selectedSheets: string[] = [];
	let isProcessing = false;
	let processResults: any[] = [];
	let errorMessage = '';

	// Load saved skip rows preference
	$: if (typeof window !== 'undefined') {
		const saved = localStorage.getItem('excel_tool_skip_rows');
		if (saved) skipRows = parseInt(saved);
	}

	function saveSkipRowsPreference() {
		if (typeof window !== 'undefined') {
			localStorage.setItem('excel_tool_skip_rows', skipRows.toString());
		}
	}

	function handleFileSelect(file: File) {
		selectedFile = file;
		uploadResponse = null;
		processResults = [];
		errorMessage = '';
	}

	async function handleUpload() {
		if (!selectedFile) return;

		isUploading = true;
		errorMessage = '';
		saveSkipRowsPreference();

		try {
			const response = await uploadFile(selectedFile, skipRows);
			
			if (response.success) {
				uploadResponse = response;
				
				if (response.multiple_sheets && response.sheets) {
					selectedSheets = [response.sheets[0]];
				}
			} else {
				errorMessage = response.error || 'Upload failed';
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Upload failed';
		} finally {
			isUploading = false;
		}
	}

	function toggleSheet(sheet: string) {
		if (selectedSheets.includes(sheet)) {
			selectedSheets = selectedSheets.filter(s => s !== sheet);
		} else {
			selectedSheets = [...selectedSheets, sheet];
		}
	}

	async function handleDownloadAll() {
		if (!uploadResponse?.temp_file || !uploadResponse?.original_filename) return;

		isProcessing = true;
		errorMessage = '';

		try {
			const response = await downloadZip({
				temp_file: uploadResponse.temp_file,
				skip_rows: uploadResponse.skip_rows || 0,
				original_filename: uploadResponse.original_filename
			});

			if (response.success && response.download_url) {
				window.location.href = getDownloadUrl(response.filename!);
				uploadResponse = null;
				selectedFile = null;
			} else {
				errorMessage = response.error || 'ZIP creation failed';
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'ZIP creation failed';
		} finally {
			isProcessing = false;
		}
	}

	async function handleDownloadSelected() {
		if (!uploadResponse?.temp_file || !uploadResponse?.original_filename || selectedSheets.length === 0) return;

		isProcessing = true;
		errorMessage = '';

		try {
			// If only one sheet selected, use quick download path
			if (selectedSheets.length === 1) {
				await handleQuickDownload(selectedSheets[0]);
				return;
			}

			// For multiple sheets, download as ZIP directly
			const response = await downloadZip({
				temp_file: uploadResponse.temp_file,
				selected_sheets: selectedSheets,
				skip_rows: uploadResponse.skip_rows || 0,
				original_filename: uploadResponse.original_filename
			});

			if (response.success && response.download_url) {
				window.location.href = getDownloadUrl(response.filename!);
				uploadResponse = null;
				selectedFile = null;
			} else {
				errorMessage = response.error || 'Download failed';
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Download failed';
		} finally {
			isProcessing = false;
		}
	}

	async function handleQuickDownload(sheet: string) {
		if (!uploadResponse?.temp_file || !uploadResponse?.original_filename) return;

		isProcessing = true;
		errorMessage = '';

		try {
			const response = await processSheets({
				temp_file: uploadResponse.temp_file,
				selected_sheets: [sheet],
				skip_rows: uploadResponse.skip_rows || 0,
				original_filename: uploadResponse.original_filename
			});

			if (response.success && response.results.length > 0) {
				const result = response.results[0];
				if (result.filename) {
					// Download immediately
					window.location.href = getDownloadUrl(result.filename);
				}
			} else {
				errorMessage = response.error || 'Download failed';
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Download failed';
		} finally {
			isProcessing = false;
		}
	}

	function handleDownload(filename: string) {
		window.location.href = getDownloadUrl(filename);
	}

	function resetForm() {
		selectedFile = null;
		uploadResponse = null;
		processResults = [];
		selectedSheets = [];
		errorMessage = '';
	}
</script>

<svelte:head>
	<title>Excel to CSV Converter</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
	<div class="max-w-4xl mx-auto space-y-6">
		<!-- Header -->
		<div class="text-center space-y-2">
			<div class="flex items-center justify-center gap-3">
				<FileSpreadsheet class="w-10 h-10 text-primary" />
				<h1 class="text-4xl font-bold tracking-tight">Excel Processor</h1>
			</div>
			<p class="text-muted-foreground">Convert Excel files to CSV with multi-sheet support</p>
		</div>

		<!-- Main Upload Card -->
		<Card>
			<CardHeader>
				<CardTitle>Upload Excel File</CardTitle>
				<CardDescription>Select an Excel file to convert to CSV format</CardDescription>
			</CardHeader>
			<CardContent class="space-y-6">
				<!-- File Upload Zone -->
				<FileUploadZone {selectedFile} onFileSelect={handleFileSelect} />

				<!-- Skip Rows Input -->
				<div class="space-y-2">
					<Label for="skip-rows">Rows to Skip</Label>
					<Input
						id="skip-rows"
						type="number"
						bind:value={skipRows}
						min="0"
						max="100"
						onchange={saveSkipRowsPreference}
						class="max-w-xs"
					/>
					<p class="text-sm text-muted-foreground">Number of header rows to ignore</p>
				</div>

				<!-- Upload Button -->
				<button
					on:click={handleUpload}
					disabled={!selectedFile || isUploading}
					class="w-full h-10 px-6 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm font-medium text-sm inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none transition-colors"
				>
					{#if isUploading}
						<Loader2 class="w-4 h-4 mr-2 animate-spin" />
						Processing...
					{:else}
						<Upload class="w-4 h-4 mr-2" />
						Process File
					{/if}
				</button>
			</CardContent>
		</Card>

		<!-- Error Message -->
		{#if errorMessage}
			<Alert variant="destructive">
				<AlertCircle class="h-4 w-4" />
				<AlertDescription>{errorMessage}</AlertDescription>
			</Alert>
		{/if}

		<!-- Single Sheet Result -->
		{#if uploadResponse?.single_sheet && uploadResponse.stats}
			<SingleSheetResult {uploadResponse} onDownload={handleDownload} onReset={resetForm} />
		{/if}

		<!-- Multiple Sheets Selection -->
		{#if uploadResponse?.multiple_sheets && uploadResponse.sheets}
			<SheetSelector
				sheets={uploadResponse.sheets}
				{selectedSheets}
				{isProcessing}
				onToggleSheet={toggleSheet}
				onDownloadAll={handleDownloadAll}
				onDownloadSelected={handleDownloadSelected}
				onQuickDownload={handleQuickDownload}
			/>
		{/if}

		<!-- Process Results -->
		{#if processResults.length > 0}
			<ProcessResults
				results={processResults}
				onDownload={handleDownload}
				onReset={resetForm}
			/>
		{/if}

		<!-- Footer -->
		<div class="text-center text-sm text-muted-foreground">
			<p>Built with FastAPI + SvelteKit + shadcn-svelte</p>
		</div>
	</div>
</div>

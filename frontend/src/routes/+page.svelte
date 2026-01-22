<script lang="ts">
	import { uploadFile, processSheets, downloadZip, getDownloadUrl } from '$lib/api';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { FileSpreadsheet, Upload, Loader2, AlertCircle, Package } from 'lucide-svelte';
	
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

<div class="min-h-screen bg-background text-foreground selection:bg-primary/30 antialiased">
	<!-- Background Ambient Glow -->
	<div class="fixed inset-0 overflow-hidden pointer-events-none">
		<div class="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-primary/10 blur-[150px] rounded-full"></div>
		<div class="absolute top-[20%] -right-[5%] w-[40%] h-[40%] bg-primary/5 blur-[120px] rounded-full"></div>
		<div class="absolute -bottom-[10%] left-[20%] w-[45%] h-[45%] bg-primary/5 blur-[130px] rounded-full"></div>
	</div>

	<div class="relative z-10 p-4 md:p-8 lg:p-12">
		<div class="max-w-[1400px] mx-auto space-y-8">
			<!-- Header -->
			<header class="flex items-center justify-between mb-12">
				<div class="flex items-center gap-4">
					<div class="p-3 bg-primary/20 rounded-2xl border border-primary/30 backdrop-blur-md shadow-lg shadow-primary/10">
						<FileSpreadsheet class="w-8 h-8 text-primary" />
					</div>
					<div>
						<h1 class="text-3xl font-extrabold bg-clip-text">
							Excel Processor <span class="text-primary text-lg ml-1 font-mono drop-shadow-sm">v2.2</span>
						</h1>
						<p class="text-muted-foreground text-sm font-medium">Professional Data Stream Management</p>
					</div>
				</div>
				<div class="hidden md:flex items-center gap-3 px-5 py-2.5 bg-muted/40 rounded-full border border-border/50 backdrop-blur-xl shadow-inner">
					<div class="w-2.5 h-2.5 rounded-full bg-primary animate-pulse shadow-[0_0_10px_rgba(var(--primary),0.8)]"></div>
					<span class="text-xs font-bold text-foreground tracking-wider uppercase">System Active</span>
				</div>
			</header>

			<div class="grid lg:grid-cols-12 gap-8 items-start">
				<!-- Left Column: Sidebar/Config -->
				<aside class="lg:col-span-4 space-y-6 lg:sticky lg:top-8">
					<Card class="bg-card/40 border-border/50 backdrop-blur-xl shadow-2xl overflow-hidden group">
						<div class="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
						<CardHeader>
							<CardTitle class="text-lg flex items-center gap-2">
								<Upload class="w-4 h-4 text-primary" />
								Source Configuration
							</CardTitle>
							<CardDescription class="text-muted-foreground">Configure your data extraction parameters</CardDescription>
						</CardHeader>
						<CardContent class="space-y-8 relative">
							<!-- File Upload Zone -->
							<FileUploadZone {selectedFile} onFileSelect={handleFileSelect} />

							<!-- Skip Rows Input -->
							<div class="space-y-4 p-4 rounded-xl bg-muted/40 border border-border/60">
								<div class="flex items-center justify-between">
									<Label for="skip-rows" class="text-foreground/80 font-medium">Header Sensitivity</Label>
									<Badge variant="outline" class="bg-primary/20 text-primary border-transparent text-[10px] font-bold uppercase tracking-wider italic">Rows to Skip</Badge>
								</div>
								<div class="flex gap-4 items-center">
									<Input
										id="skip-rows"
										type="number"
										bind:value={skipRows}
										min="0"
										max="100"
										onchange={saveSkipRowsPreference}
										class="bg-muted/60 border-border focus-visible:ring-primary/50 text-lg font-mono"
									/>
									<div class="text-muted-foreground text-xs leading-tight">
										Recommended: <span class="text-foreground/70">8-10</span> for standard reports
									</div>
								</div>
							</div>

							<!-- Upload Button -->
							<Button
								onclick={handleUpload}
								disabled={!selectedFile || isUploading}
								size="lg"
								class="w-full h-14 rounded-xl font-bold text-base flex items-center justify-center gap-3 transition-all active:scale-[0.98] disabled:opacity-30 disabled:pointer-events-none hover:shadow-[0_0_30px_-5px_rgba(var(--primary),0.5)] group/btn"
							>
								{#if isUploading}
									<Loader2 class="w-5 h-5 animate-spin" />
									<span>ANALYZING DATA...</span>
								{:else}
									<Upload class="w-5 h-5 group-hover/btn:-translate-y-1 transition-transform" />
									<span>INITIALIZE PROCESS</span>
								{/if}
							</Button>
						</CardContent>
					</Card>

					<!-- Status Card -->
					<div class="p-6 rounded-2xl bg-card border border-border/40 backdrop-blur-md">
						<h3 class="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-4">Operations Status</h3>
						<div class="space-y-3">
							<div class="flex items-center justify-between text-sm">
								<span class="text-muted-foreground">Memory Usage</span>
								<span class="text-foreground/90">Normal</span>
							</div>
							<div class="w-full h-1 bg-secondary rounded-full overflow-hidden">
								<div class="w-1/3 h-full bg-primary/60"></div>
							</div>
							<div class="flex items-center justify-between text-sm mt-4">
								<span class="text-muted-foreground">API Latency</span>
								<span class="text-green-500">24ms</span>
							</div>
						</div>
					</div>
				</aside>

				<!-- Right Column: Results/Workspace -->
				<main class="lg:col-span-8 space-y-6">
					<!-- Error Message -->
					{#if errorMessage}
						<Alert variant="destructive" class="bg-red-500/10 border-red-500/20 text-red-400 animate-in fade-in slide-in-from-top-4">
							<AlertCircle class="h-5 w-5" />
							<AlertDescription class="font-medium">{errorMessage}</AlertDescription>
						</Alert>
					{/if}

					{#if !uploadResponse && processResults.length === 0 && !isUploading}
						<div class="h-[600px] rounded-3xl border border-border border-dashed flex flex-col items-center justify-center text-muted-foreground bg-muted/5">
							<div class="p-10 rounded-full bg-muted/10 mb-6 border border-border/20">
								<Package class="w-16 h-16 opacity-40 text-primary" />
							</div>
							<p class="font-bold text-xl tracking-wide text-foreground">System Ready</p>
							<p class="text-sm text-muted-foreground/60 mt-2">Awaiting source initialization...</p>
						</div>
					{/if}

					{#if isUploading && !uploadResponse}
						<div class="h-[600px] rounded-3xl border border-border/40 bg-muted/10 flex flex-col items-center justify-center">
							<div class="relative">
								<div class="w-24 h-24 border-4 border-primary/10 border-t-primary rounded-full animate-spin"></div>
								<div class="absolute inset-0 flex items-center justify-center">
									<Loader2 class="w-8 h-8 text-primary animate-pulse" />
								</div>
							</div>
							<p class="mt-8 text-primary font-bold tracking-widest animate-pulse">PROCESSING DATASTREAM</p>
						</div>
					{/if}

					<!-- Single Sheet Result -->
					{#if uploadResponse?.single_sheet && uploadResponse.stats}
						<div class="animate-in fade-in zoom-in-95 duration-500">
							<SingleSheetResult {uploadResponse} onDownload={handleDownload} onReset={resetForm} />
						</div>
					{/if}

					<!-- Multiple Sheets Selection -->
					{#if uploadResponse?.multiple_sheets && uploadResponse.sheets}
						<div class="animate-in fade-in slide-in-from-right-8 duration-500">
							<SheetSelector
								sheets={uploadResponse.sheets}
								{selectedSheets}
								{isProcessing}
								onToggleSheet={toggleSheet}
								onDownloadAll={handleDownloadAll}
								onDownloadSelected={handleDownloadSelected}
								onQuickDownload={handleQuickDownload}
							/>
						</div>
					{/if}

					<!-- Process Results -->
					{#if processResults.length > 0}
						<div class="animate-in fade-in slide-in-from-bottom-8 duration-500">
							<ProcessResults
								results={processResults}
								onDownload={handleDownload}
								onReset={resetForm}
							/>
						</div>
					{/if}
				</main>
			</div>

			<!-- Footer -->
			<footer class="mt-24 pt-8 border-t border-border/50 flex flex-col md:flex-row items-center justify-between gap-4 text-muted-foreground text-xs">
				<p>© 2026 Advanced Agentic Coding - Excel Processor Engine. All rights reserved.</p>
				<div class="flex items-center gap-6">
					<span class="flex items-center gap-2 hover:text-foreground transition-colors cursor-pointer">
						<div class="w-1 h-1 rounded-full bg-muted-foreground"></div> Documentation
					</span>
					<span class="flex items-center gap-2 hover:text-foreground transition-colors cursor-pointer">
						<div class="w-1 h-1 rounded-full bg-muted-foreground"></div> API Reference
					</span>
					<div class="px-2 py-0.5 rounded border border-border bg-muted">v2.1.0-STABLE</div>
				</div>
			</footer>
		</div>
	</div>
</div>

<style>
	:global(body) {
		font-family: 'Inter', system-ui, -apple-system, sans-serif;
	}

	:global(.card) {
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	:global(.card:hover) {
		border-color: rgba(var(--primary-rgb), 0.3) !important;
		transform: translateY(-2px);
	}
</style>

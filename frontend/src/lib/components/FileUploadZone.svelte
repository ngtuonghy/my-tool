<script lang="ts">
	import { Upload, FileSpreadsheet } from 'lucide-svelte';
	import { Label } from '$lib/components/ui/label';

	export let selectedFile: File | null = null;
	export let onFileSelect: (file: File) => void;

	let fileInput: HTMLInputElement;

	// Reset file input when selectedFile is cleared
	$: if (selectedFile === null && fileInput) {
		fileInput.value = '';
	}

	function handleFileChange(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			onFileSelect(target.files[0]);
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
			onFileSelect(event.dataTransfer.files[0]);
		}
	}

	function handleClick() {
		fileInput?.click();
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			fileInput?.click();
		}
	}
</script>

<div class="space-y-3">
	<div
		role="button"
		tabindex="0"
		class="relative group border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-300 bg-muted/40 border-border/80 hover:border-primary/50 hover:bg-muted/60 overflow-hidden"
		on:dragover={handleDragOver}
		on:drop={handleDrop}
		on:click={handleClick}
		on:keydown={handleKeyDown}
	>
		<!-- Animated Background Shine -->
		<div class="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
		
		<input
			bind:this={fileInput}
			id="file-upload"
			type="file"
			accept=".xls,.xlsx"
			class="hidden"
			on:change={handleFileChange}
		/>

		{#if selectedFile}
			<div class="relative z-10 animate-in fade-in zoom-in-95 duration-300">
				<div class="w-12 h-12 mx-auto mb-3 bg-primary/20 rounded-xl flex items-center justify-center border border-primary/30">
					<FileSpreadsheet class="w-6 h-6 text-primary" />
				</div>
				<p class="font-bold text-foreground truncate px-2">{selectedFile.name}</p>
				<p class="text-[10px] font-mono text-muted-foreground mt-1 uppercase tracking-tighter">
					BLOCK SIZE: {(selectedFile.size / 1024).toFixed(0)} KB
				</p>
			</div>
		{:else}
			<div class="relative z-10 py-2">
				<div class="w-12 h-12 mx-auto mb-4 bg-muted rounded-xl flex items-center justify-center border border-border group-hover:border-primary/30 group-hover:scale-110 transition-all duration-300">
					<Upload class="w-6 h-6 text-muted-foreground group-hover:text-primary" />
				</div>
				<p class="font-semibold text-muted-foreground group-hover:text-foreground transition-colors">DRAG & DROP SOURCE</p>
				<p class="text-[10px] text-muted-foreground/60 mt-2 uppercase tracking-[0.2em]">Supported: .XLS, .XLSX</p>
			</div>
		{/if}
	</div>
</div>


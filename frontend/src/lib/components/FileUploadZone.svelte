<script lang="ts">
	import { Upload } from 'lucide-svelte';
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

<div class="space-y-2">
	<Label for="file-upload">Excel File</Label>
	<div
		role="button"
		tabindex="0"
		class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-primary hover:bg-accent/50"
		on:dragover={handleDragOver}
		on:drop={handleDrop}
		on:click={handleClick}
		on:keydown={handleKeyDown}
	>
		<input
			bind:this={fileInput}
			id="file-upload"
			type="file"
			accept=".xls,.xlsx"
			class="hidden"
			on:change={handleFileChange}
		/>
		<Upload class="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
		{#if selectedFile}
			<p class="font-medium text-primary">{selectedFile.name}</p>
			<p class="text-sm text-muted-foreground mt-1">
				{(selectedFile.size / 1024 / 1024).toFixed(2)} MB
			</p>
		{:else}
			<p class="font-medium">Click to browse or drag and drop</p>
			<p class="text-sm text-muted-foreground mt-1">Excel files (.xls, .xlsx)</p>
		{/if}
	</div>
</div>

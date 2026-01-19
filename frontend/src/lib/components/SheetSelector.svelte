<script lang="ts">
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { Separator } from '$lib/components/ui/separator';
	import { Button } from '$lib/components/ui/button';
	import { Package, Download, Loader2 } from 'lucide-svelte';

	export let sheets: string[];
	export let selectedSheets: string[];
	export let isProcessing: boolean = false;
	export let onToggleSheet: (sheet: string) => void;
	export let onDownloadAll: () => void;
	export let onDownloadSelected: () => void;
	export let onQuickDownload: (sheet: string) => void;
</script>

<Card>
	<CardHeader>
		<div class="flex items-center justify-between">
			<div>
				<CardTitle>Multiple Sheets Detected</CardTitle>
				<CardDescription>Select sheets to process</CardDescription>
			</div>
			<Badge variant="secondary">{sheets.length} sheets</Badge>
		</div>
	</CardHeader>
	<CardContent class="space-y-4">
		<!-- Sheet List -->
		<div class="space-y-2 max-h-60 overflow-y-auto">
			{#each sheets as sheet}
				<div class="flex items-center gap-3 p-3 border rounded-lg hover:bg-accent transition-colors">
					<label class="flex items-center gap-3 flex-1 cursor-pointer">
						<input
							type="checkbox"
							checked={selectedSheets.includes(sheet)}
							onchange={() => onToggleSheet(sheet)}
							class="w-4 h-4"
						/>
						<span class="font-medium">{sheet}</span>
					</label>
					<button
						onclick={() => onQuickDownload(sheet)}
						class="h-8 px-3 rounded-md border bg-background hover:bg-accent hover:text-accent-foreground shadow-sm font-medium text-xs inline-flex items-center justify-center gap-1 disabled:opacity-50 disabled:pointer-events-none transition-colors"
						title="Download this sheet only"
					>
						<Download class="w-3 h-3" />
						Quick
					</button>
				</div>
			{/each}
		</div>

		<Separator />

		<!-- Action Buttons -->
		<div class="grid grid-cols-2 gap-3">
			<Button
				onclick={onDownloadAll}
				disabled={isProcessing}
				variant="default"
				size="lg"
			>
				{#if isProcessing}
					<Loader2 class="w-4 h-4 mr-2 animate-spin" />
				{:else}
					<Package class="w-4 h-4 mr-2" />
				{/if}
				Download All (ZIP)
			</Button>
			<Button
				onclick={onDownloadSelected}
				disabled={selectedSheets.length === 0 || isProcessing}
				variant="secondary"
				size="lg"
			>
				{#if isProcessing}
					<Loader2 class="w-4 h-4 mr-2 animate-spin" />
				{:else}
					<Download class="w-4 h-4 mr-2" />
				{/if}
				Download Selected ({selectedSheets.length})
			</Button>
		</div>
	</CardContent>
</Card>

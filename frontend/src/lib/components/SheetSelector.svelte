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

<Card class="bg-card/40 border-border/50 backdrop-blur-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-8">
	<CardHeader class="pb-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-primary/10 rounded-lg border border-primary/20">
					<Package class="w-5 h-5 text-primary" />
				</div>
				<div>
					<CardTitle class="text-xl font-bold bg-gradient-to-r from-white to-foreground/70 bg-clip-text text-transparent">Multi-Sheet Stream</CardTitle>
					<CardDescription class="text-muted-foreground">Select target sheets for extraction</CardDescription>
				</div>
			</div>
			<Badge variant="outline" class="bg-muted/50 border-border text-muted-foreground font-mono">
				{sheets.length} CHANNELS
			</Badge>
		</div>
	</CardHeader>
	<CardContent class="space-y-6">
		<!-- Sheet List -->
		<div class="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
			{#each sheets as sheet}
				<div class="group flex items-center gap-3 p-4 bg-muted/40 border border-border/60 rounded-xl hover:border-primary/30 hover:bg-muted/60 transition-all duration-300">
					<label class="flex items-center gap-4 flex-1 cursor-pointer">
						<div class="relative flex items-center justify-center">
							<input
								type="checkbox"
								checked={selectedSheets.includes(sheet)}
								onchange={() => onToggleSheet(sheet)}
								class="peer appearance-none w-5 h-5 border-2 border-border rounded-md checked:bg-primary checked:border-primary transition-all cursor-pointer"
							/>
							<div class="absolute text-background opacity-0 peer-checked:opacity-100 transition-opacity">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 font-bold" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="4">
									<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
								</svg>
							</div>
						</div>
						<span class="font-medium text-muted-foreground group-hover:text-foreground transition-colors uppercase tracking-tight font-mono text-sm">{sheet}</span>
					</label>
					<Button
						variant="outline"
						size="sm"
						onclick={() => onQuickDownload(sheet)}
						class="h-9 px-4 rounded-lg bg-muted border-border hover:bg-primary hover:text-primary-foreground hover:border-primary shadow-sm font-bold text-[10px] uppercase tracking-widest inline-flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50"
						title="Quick Extract"
					>
						<Download class="w-3.5 h-3.5" />
						Quick
					</Button>
				</div>
			{/each}
		</div>

		<div class="h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>

		<!-- Action Buttons -->
		<div class="grid grid-cols-2 gap-4">
			<Button
				variant="outline"
				onclick={onDownloadAll}
				disabled={isProcessing}
				class="h-14 rounded-xl bg-background border-border hover:border-muted-foreground/50 text-foreground font-bold text-sm flex items-center justify-center gap-3 transition-all active:scale-[0.98] disabled:opacity-30"
			>
				{#if isProcessing}
					<Loader2 class="w-5 h-5 animate-spin" />
				{:else}
					<Package class="w-5 h-5 text-muted-foreground" />
				{/if}
				EXTRACT ALL (ZIP)
			</Button>
			<Button
				onclick={onDownloadSelected}
				disabled={selectedSheets.length === 0 || isProcessing}
				class="h-14 rounded-xl bg-primary text-primary-foreground font-bold text-sm flex items-center justify-center gap-3 transition-all active:scale-[0.98] disabled:opacity-30 hover:shadow-[0_0_20px_-5px_rgba(var(--primary),0.4)]"
			>
				{#if isProcessing}
					<Loader2 class="w-5 h-5 animate-spin text-primary-foreground" />
				{:else}
					<Download class="w-5 h-5" />
				{/if}
				EXTRACT SELECTED ({selectedSheets.length})
			</Button>
		</div>
	</CardContent>
</Card>

<style>
	.custom-scrollbar::-webkit-scrollbar {
		width: 4px;
	}
	.custom-scrollbar::-webkit-scrollbar-track {
		background: transparent;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb {
		background: #1e293b;
		border-radius: 10px;
	}
	.custom-scrollbar::-webkit-scrollbar-thumb:hover {
		background: #334155;
	}
</style>

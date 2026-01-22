<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { Badge } from '$lib/components/ui/badge';
	import { Separator } from '$lib/components/ui/separator';
	import { Button } from '$lib/components/ui/button';
	import { CheckCircle2, Download, Package } from 'lucide-svelte';
	import type { SheetResult } from '$lib/api';

	export let results: SheetResult[];
	export let onDownload: (filename: string) => void;
	export let onReset: () => void;
</script>

<Card class="bg-card/40 border-border/50 backdrop-blur-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-8">
	<CardHeader class="pb-6">
		<div class="flex items-center gap-4">
			<div class="p-3 bg-green-500/10 rounded-2xl border border-green-500/20">
				<CheckCircle2 class="w-6 h-6 text-green-500" />
			</div>
			<div>
				<CardTitle class="text-2xl font-bold bg-gradient-to-r from-white to-foreground/70 bg-clip-text text-transparent">{results.length} Streams Processed</CardTitle>
				<p class="text-muted-foreground text-sm italic">Multi-channel extraction complete</p>
			</div>
		</div>
	</CardHeader>
	<CardContent class="space-y-4">
		<div class="grid gap-3">
			{#each results as result}
				<div class="group relative overflow-hidden flex flex-col p-4 bg-muted/40 border border-border/60 rounded-2xl hover:border-primary/30 hover:bg-muted/40 transition-all duration-300">
					<div class="flex items-center justify-between mb-3">
						<div class="flex items-center gap-3">
							<div class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
							<p class="font-bold text-foreground/90 tracking-tight uppercase text-xs font-mono">{result.sheet_name}</p>
						</div>
						{#if result.stats}
							<Badge variant="outline" class="bg-muted/50 border-border text-muted-foreground text-[10px] font-mono">
								{result.stats.original_rows} ROWS
							</Badge>
						{/if}
					</div>
					
					{#if result.error}
						<Alert variant="destructive" class="bg-red-500/10 border-red-500/20 text-red-500 text-xs py-2">
							<AlertDescription>{result.error}</AlertDescription>
						</Alert>
					{:else if result.download_url}
						<Button
							variant="outline"
							size="sm"
							onclick={() => onDownload(result.filename!)}
							class="w-full h-11 rounded-xl bg-muted border-border hover:border-primary/50 hover:bg-primary/10 hover:text-primary text-foreground font-bold text-xs flex items-center justify-center gap-2 transition-all active:scale-[0.98]"
						>
							<Download class="w-4 h-4" />
							RETRIEVE CSV
						</Button>
					{/if}
				</div>
			{/each}
		</div>

		<div class="h-px bg-gradient-to-r from-transparent via-border to-transparent my-6"></div>

		<Button
			variant="outline"
			onclick={onReset}
			class="w-full h-14 rounded-2xl bg-muted/30 border-border hover:bg-muted/50 hover:border-muted-foreground/50 text-muted-foreground font-bold text-sm tracking-widest flex items-center justify-center gap-3 transition-all active:scale-[0.98] uppercase"
		>
			<Package class="w-5 h-5 opacity-40" />
			Initialize New Process
		</Button>
	</CardContent>
</Card>

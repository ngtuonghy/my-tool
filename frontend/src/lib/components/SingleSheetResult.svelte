<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Separator } from '$lib/components/ui/separator';
	import { Button } from '$lib/components/ui/button';
	import { CheckCircle2, Download } from 'lucide-svelte';
	import type { UploadResponse } from '$lib/api';

	export let uploadResponse: UploadResponse;
	export let onDownload: (filename: string) => void;
	export let onReset: () => void;
</script>

{#if uploadResponse.stats}
	<Card class="bg-card/40 border-border/50 backdrop-blur-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95">
		<CardHeader class="pb-6">
			<div class="flex items-center gap-4">
				<div class="p-3 bg-green-500/10 rounded-2xl border border-green-500/20">
					<CheckCircle2 class="w-6 h-6 text-green-500" />
				</div>
				<div>
					<CardTitle class="text-2xl font-bold bg-gradient-to-r from-white to-foreground/70 bg-clip-text text-transparent">Extract Successful</CardTitle>
					<p class="text-muted-foreground text-sm italic">Direct CSV stream generated</p>
				</div>
			</div>
		</CardHeader>
		<CardContent class="space-y-8">
			<div class="grid grid-cols-2 md:grid-cols-4 gap-6">
				<div class="p-4 rounded-xl bg-muted/60 border border-border/60">
					<p class="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Row count</p>
					<p class="text-3xl font-mono font-bold text-foreground">{uploadResponse.stats.original_rows}</p>
				</div>
				<div class="p-4 rounded-xl bg-muted/60 border border-border/60">
					<p class="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Col density</p>
					<p class="text-3xl font-mono font-bold text-foreground">{uploadResponse.stats.final_columns}</p>
				</div>
				<div class="p-4 rounded-xl bg-muted/60 border border-border/60">
					<p class="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Optimizations</p>
					<p class="text-3xl font-mono font-bold text-foreground">{uploadResponse.stats.empty_columns_removed}</p>
				</div>
				<div class="p-4 rounded-xl bg-muted/60 border border-border/60">
					<p class="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">Map events</p>
					<p class="text-3xl font-mono font-bold text-foreground">{uploadResponse.stats.unnamed_columns_renamed}</p>
				</div>
			</div>

			<div class="h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>

			<div class="grid grid-cols-2 gap-4">
				<Button
					onclick={() => onDownload(uploadResponse.filename!)}
					class="h-14 rounded-xl bg-primary text-primary-foreground font-bold text-base flex items-center justify-center gap-3 transition-all active:scale-[0.98] hover:shadow-[0_0_20px_-5px_rgba(var(--primary),0.5)]"
				>
					<Download class="w-5 h-5" />
					DOWNLOAD CSV
				</Button>
				<Button
					variant="outline"
					onclick={onReset}
					class="h-14 rounded-xl bg-background border-border hover:border-muted-foreground/50 text-foreground font-bold text-sm flex items-center justify-center gap-3 transition-all active:scale-[0.98]"
				>
					PROCESS ANOTHER
				</Button>
			</div>
		</CardContent>
	</Card>
{/if}

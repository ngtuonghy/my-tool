<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Separator } from '$lib/components/ui/separator';
	import { CheckCircle2, Download } from 'lucide-svelte';
	import type { UploadResponse } from '$lib/api';

	export let uploadResponse: UploadResponse;
	export let onDownload: (filename: string) => void;
	export let onReset: () => void;
</script>

{#if uploadResponse.stats}
	<Card>
		<CardHeader>
			<div class="flex items-center gap-2">
				<CheckCircle2 class="w-5 h-5 text-green-600" />
				<CardTitle>Processing Complete</CardTitle>
			</div>
		</CardHeader>
		<CardContent class="space-y-4">
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="space-y-1">
					<p class="text-sm text-muted-foreground">Rows</p>
					<p class="text-2xl font-bold">{uploadResponse.stats.original_rows}</p>
				</div>
				<div class="space-y-1">
					<p class="text-sm text-muted-foreground">Columns</p>
					<p class="text-2xl font-bold">{uploadResponse.stats.final_columns}</p>
				</div>
				<div class="space-y-1">
					<p class="text-sm text-muted-foreground">Cleaned</p>
					<p class="text-2xl font-bold">{uploadResponse.stats.empty_columns_removed}</p>
				</div>
				<div class="space-y-1">
					<p class="text-sm text-muted-foreground">Renamed</p>
					<p class="text-2xl font-bold">{uploadResponse.stats.unnamed_columns_renamed}</p>
				</div>
			</div>
			<Separator />
			<div class="grid grid-cols-2 gap-3">
				<button
					onclick={() => onDownload(uploadResponse.filename!)}
					class="h-10 px-6 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm font-medium text-sm inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none transition-colors"
				>
					<Download class="w-4 h-4 mr-2" />
					Download CSV
				</button>
				<button
					onclick={onReset}
					class="h-10 px-6 rounded-md border bg-background hover:bg-accent hover:text-accent-foreground shadow-sm font-medium text-sm inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none transition-colors"
				>
					Process Another File
				</button>
			</div>
		</CardContent>
	</Card>
{/if}

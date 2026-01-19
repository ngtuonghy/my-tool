<script lang="ts">
	import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { Alert, AlertDescription } from '$lib/components/ui/alert';
	import { Badge } from '$lib/components/ui/badge';
	import { Separator } from '$lib/components/ui/separator';
	import { Button } from '$lib/components/ui/button';
	import { CheckCircle2, Download } from 'lucide-svelte';
	import type { SheetResult } from '$lib/api';

	export let results: SheetResult[];
	export let onDownload: (filename: string) => void;
	export let onReset: () => void;
</script>

<Card>
	<CardHeader>
		<div class="flex items-center gap-2">
			<CheckCircle2 class="w-5 h-5 text-green-600" />
			<CardTitle>{results.length} Sheet(s) Processed</CardTitle>
		</div>
	</CardHeader>
	<CardContent class="space-y-3">
		{#each results as result}
			<div class="border rounded-lg p-4 space-y-3">
				<div class="flex items-center justify-between">
					<p class="font-semibold">{result.sheet_name}</p>
					{#if result.stats}
						<Badge variant="outline">{result.stats.original_rows} rows</Badge>
					{/if}
				</div>
				{#if result.error}
					<Alert variant="destructive">
						<AlertDescription>{result.error}</AlertDescription>
					</Alert>
				{:else if result.download_url}
					<Button
						onclick={() => onDownload(result.filename!)}
						variant="outline"
						class="w-full"
					>
						<Download class="w-4 h-4 mr-2" />
						Download CSV
					</Button>
				{/if}
			</div>
		{/each}
		<Separator />
		<Button onclick={onReset} variant="outline" class="w-full">
			Process Another File
		</Button>
	</CardContent>
</Card>

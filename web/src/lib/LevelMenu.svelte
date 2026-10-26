<script>
  // the level pill; its menu lists every released level with its age and summary
  let { levels, level = $bindable() } = $props()
  let open = $state(false)
  let root

  const card = $derived(levels.find((l) => l.id === level))

  function pick(id) { level = id; open = false }
</script>

<svelte:window
  onclick={(e) => open && !root.contains(e.target) && (open = false)}
  onkeydown={(e) => e.key === 'Escape' && (open = false)}
/>

<div class="wrap" bind:this={root}>
  <button class="pill" class:open disabled={!levels.length} onclick={() => (open = !open)} aria-haspopup="listbox" aria-expanded={open}>
    {#if card}<span>{card.id}</span><span class="dim">{card.name}</span>{:else}<span class="dim">no level yet</span>{/if}
    <svg class="caret" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" /></svg>
  </button>
  {#if open}
    <div class="menu" role="listbox">
      {#each levels as l (l.id)}
        <button class="item" class:on={l.id === level} role="option" aria-selected={l.id === level} onclick={() => pick(l.id)}>
          <div class="text">
            <div class="name">{l.id} <span class="dim">· {l.name}</span></div>
            <div class="about">like a {l.human_age} · {l.summary}</div>
          </div>
          {#if l.id === level}<div class="check">✓</div>{/if}
        </button>
      {/each}
      <div class="note">Next level unlocks when it passes the next stage.</div>
    </div>
  {/if}
</div>

<style>
  .wrap { position: relative; }
  .pill { display: flex; align-items: center; gap: 6px; border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px 4px 12px; font-size: 13px; }
  .pill:hover:not(:disabled), .pill.open { border-color: var(--edge); background: var(--panel); }
  .dim { color: var(--dim); }
  .caret { width: 9px; height: 6px; fill: none; stroke: var(--dim); stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
  .open .caret { transform: rotate(180deg); }
  .menu { position: absolute; top: calc(100% + 8px); left: 0; z-index: 2; width: 300px; max-width: calc(100vw - 32px); background: var(--panel);
    border: 1px solid var(--line); border-radius: 12px; padding: 6px; display: flex; flex-direction: column; gap: 2px; box-shadow: 0 12px 32px rgba(0, 0, 0, .5); }
  .item { display: flex; gap: 10px; padding: 10px; border-radius: 8px; text-align: left; }
  .item:hover, .item.on { background: var(--me); }
  .text { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
  .name { font-size: 14px; }
  .about { font-size: 12px; color: var(--dim); text-wrap: pretty; }
  .check { font-size: 13px; }
  .note { padding: 8px 10px; font-size: 12px; color: var(--faint); }
</style>

<script>
  // one side of a turn; for the kid's replies to a picture, the picture again with where its eye looked
  let { m } = $props()
  const meta = $derived(m.who !== 'kid' ? '' : m.error ? `error: ${m.error}` :
    [`${m.ticks} ticks`, m.copied && 'repeating what it heard', m.gaze && `looked at ${m.gaze.length} ${m.gaze.length === 1 ? 'place' : 'places'}`, `${m.ms} ms`].filter(Boolean).join(' · '))
</script>

{#if m.who === 'me'}
  <div class="me">
    {#if m.image}<img src={m.image} alt="" />{/if}
    {#if m.text}<div class="bubble">{m.text}</div>{/if}
  </div>
{:else}
  <div class="kid">
    {#if m.gaze}
      <div class="eye" title="where it looked, in order">
        <img src={m.image} alt="" />
        <svg viewBox="0 0 1 1" preserveAspectRatio="none">
          <polyline points={m.gaze.map(([x, y]) => `${x},${y}`).join(' ')} />
          {#each m.gaze as [x, y], i}<circle cx={x} cy={y} r={i === 0 ? 0.035 : 0.025} class:first={i === 0} />{/each}
        </svg>
      </div>
    {/if}
    {#if m.text || !m.error}<div class="said">{m.text || '…'}</div>{/if}
    {#if meta}<div class="meta" class:error={m.error}>{meta}</div>{/if}
  </div>
{/if}

<style>
  .me { align-self: flex-end; max-width: 80%; display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
  .me img { width: 140px; height: 140px; object-fit: cover; border-radius: 12px; border: 1px solid var(--line); display: block; }
  .bubble { padding: 8px 14px; border-radius: 18px; background: var(--me); white-space: pre-wrap; overflow-wrap: anywhere; }
  .kid { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
  .said { font-size: 17px; white-space: pre-wrap; overflow-wrap: anywhere; }
  .eye { position: relative; width: 96px; height: 96px; border-radius: 10px; overflow: hidden; border: 1px solid var(--line); background: var(--panel); margin-bottom: 2px; }
  .eye img { width: 100%; height: 100%; object-fit: cover; display: block; opacity: .55; }
  svg { position: absolute; inset: 0; width: 100%; height: 100%; }
  polyline { fill: none; stroke: var(--eye); stroke-width: 0.012; opacity: .7; }
  circle { fill: var(--eye); }
  circle.first { fill: none; stroke: var(--eye); stroke-width: 0.012; }
  .meta { color: var(--faint); font-size: 12px; }
  .meta.error { color: var(--dim); }
</style>

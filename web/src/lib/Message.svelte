<script>
  // one turn; for the kid's replies to a picture, the picture again with where its eye looked
  let { m } = $props()
  const meta = $derived(m.who !== 'kid' ? '' : m.error ? `error: ${m.error}` :
    [`${m.ticks} ticks`, m.copied && 'repeating what it heard', m.gaze && `looked at ${m.gaze.length} places`, `${m.ms} ms`].filter(Boolean).join(' · '))
</script>

<div class="msg {m.who}">
  {#if m.who === 'me' && m.image}<img src={m.image} alt="" />{/if}
  {#if m.who === 'me' && m.text}<div class="bubble">{m.text}</div>{/if}
  {#if m.who === 'kid'}
    {#if m.gaze}
      <div class="eye" title="where it looked, in order">
        <img src={m.image} alt="" />
        <svg viewBox="0 0 1 1" preserveAspectRatio="none">
          <polyline points={m.gaze.map(([x, y]) => `${x},${y}`).join(' ')} />
          {#each m.gaze as [x, y], i}<circle cx={x} cy={y} r={i === 0 ? 0.035 : 0.025} class:first={i === 0} />{/each}
        </svg>
      </div>
    {/if}
    <div class="said">{m.text || (m.error ? '' : '…')}</div>
  {/if}
  {#if meta}<div class="meta">{meta}</div>{/if}
</div>

<style>
  .msg { margin: 0 0 18px; display: flex; flex-direction: column; align-items: flex-start; }
  .me { align-items: flex-end; }
  .bubble { max-width: 85%; padding: 10px 14px; border-radius: 14px; background: var(--me); white-space: pre-wrap; overflow-wrap: anywhere; }
  .said { font-size: 18px; white-space: pre-wrap; overflow-wrap: anywhere; }
  img { max-width: 220px; max-height: 220px; border-radius: 10px; margin-bottom: 6px; border: 1px solid var(--line); }
  .eye { position: relative; width: 120px; height: 120px; margin-bottom: 6px; }
  .eye img { width: 100%; height: 100%; object-fit: cover; margin: 0; opacity: .55; }
  svg { position: absolute; inset: 0; width: 100%; height: 100%; }
  polyline { fill: none; stroke: var(--eye); stroke-width: 0.012; opacity: .7; }
  circle { fill: var(--eye); }
  circle.first { fill: none; stroke: var(--eye); stroke-width: 0.012; }
  .meta { color: var(--dim); font-size: 12px; margin-top: 2px; }
</style>

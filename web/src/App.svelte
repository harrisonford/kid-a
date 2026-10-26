<script>
  import Message from './lib/Message.svelte'
  import Composer from './lib/Composer.svelte'
  import LevelMenu from './lib/LevelMenu.svelte'

  // chats live only in this browser (localStorage), one per level
  const store = {
    get: (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d } catch { return d } },
    set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)) } catch {} },
  }
  const num = (n) => n.toLocaleString('en-US')
  const short = (n) => n.toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 1 })

  let levels = $state([])
  let level = $state(store.get('kid-a:level', null))
  let history = $state([])
  let busy = $state(false)
  let scroller

  const card = $derived(levels.find((l) => l.id === level))
  // a turn is what you said and how it answered
  const turns = $derived(history.reduce((ts, m) => {
    if (m.who === 'me' || !ts.length) ts.push([])
    ts.at(-1).push(m)
    return ts
  }, []))

  $effect(() => {
    if (level) {
      store.set('kid-a:level', level)
      history = store.get(`kid-a:chat:${level}`, [])
    }
  })

  $effect(() => {
    history.length
    queueMicrotask(() => scroller && (scroller.scrollTop = scroller.scrollHeight))
  })

  fetch('/api/levels').then((r) => r.json()).then((ls) => {
    levels = ls.filter((l) => l.available)
    if (!levels.some((l) => l.id === level)) level = levels.at(-1)?.id ?? null
  })

  function keep() { store.set(`kid-a:chat:${level}`, history.slice(-200)) }

  async function send({ text, image }) {
    history.push({ who: 'me', text, image })
    keep()
    busy = true
    try {
      const r = await (await fetch('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, text, image }),
      })).json()
      if (r.error) throw new Error(r.error)
      history.push({ who: 'kid', text: r.answer, ticks: r.ticks, copied: r.copied, ms: r.ms, gaze: image ? r.gaze_xy : null, image })
    } catch (e) {
      history.push({ who: 'kid', text: '', error: e.message })
    }
    busy = false
    keep()
  }

  function clear() { history = []; keep() }
</script>

<div class="app">
  <header class:ruled={history.length}>
    <div class="mark"><img src="/favicon.svg" alt="" /><span>kid-a</span></div>
    <LevelMenu {levels} bind:level />
    <div class="grow"></div>
    <button class="clear" onclick={clear} disabled={!history.length} title="clear this chat">clear</button>
  </header>

  <main bind:this={scroller}>
    {#if !history.length}
      <div class="empty">
        <img src="/favicon.svg" alt="" />
        <div class="hello">
          <div class="lead">Talk to it like you would to a small child.</div>
          <div class="dim">It only knows what its level has learned.</div>
        </div>
        {#if card}
          <div class="facts">
            <div class="dim">can</div><div>{card.can}</div>
            <div class="dim">can't</div><div class="dim">{card.cannot}</div>
            <div class="dim">size</div>
            <div>
              {#if card.parameters != null}<span class="nb" title="{num(card.parameters)} parameters">{short(card.parameters)} parameters</span>
                <span class="dim"><span class="nb">· {num(card.clusters)} clusters</span> <span class="nb">· {num(card.moments_lived)} moments lived</span></span>
              {:else}<span class="nb">{num(card.clusters)} clusters</span> <span class="dim nb">· {num(card.moments_lived)} moments lived</span>{/if}
            </div>
          </div>
        {:else if levels.length === 0}
          <div class="dim">No level released yet.</div>
        {/if}
      </div>
    {:else}
      <div class="log">
        {#each turns as turn, i (i)}
          <div class="turn">{#each turn as m, j (j)}<Message {m} />{/each}</div>
        {/each}
        {#if busy}<div class="thinking">···</div>{/if}
      </div>
    {/if}
  </main>

  <Composer onsend={send} disabled={busy || !level} />
</div>

<style>
  .app { height: 100%; display: flex; flex-direction: column; }
  header { height: 52px; flex: none; display: flex; align-items: center; gap: 12px; padding: 0 16px; border-bottom: 1px solid transparent; }
  header.ruled { border-bottom-color: var(--hair); }
  .mark { display: flex; align-items: center; gap: 8px; font-weight: 600; letter-spacing: .5px; }
  .mark img { width: 20px; height: 20px; display: block; }
  .grow { flex: 1; }
  .clear { color: var(--dim); font-size: 13px; padding: 6px 10px; border-radius: 8px; }
  .clear:hover:not(:disabled) { color: var(--text); background: var(--panel); }
  .clear:disabled { color: var(--faint); }
  main { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
  .dim { color: var(--dim); }
  .empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; padding: 24px; }
  .empty > img { width: 40px; height: 40px; display: block; }
  .hello { display: flex; flex-direction: column; align-items: center; gap: 4px; text-align: center; }
  .lead { font-size: 17px; }
  .hello .dim { font-size: 14px; }
  .facts { max-width: 440px; display: grid; grid-template-columns: 56px 1fr; gap: 8px 12px; font-size: 13px; border-top: 1px solid var(--line); padding-top: 16px; text-wrap: pretty; }
  .nb { white-space: nowrap; }
  .log { width: 100%; max-width: 680px; margin: auto auto 0; padding: 24px 20px; display: flex; flex-direction: column; gap: 28px; }
  .turn { display: flex; flex-direction: column; gap: 12px; }
  .thinking { color: var(--dim); font-size: 17px; letter-spacing: 2px; }
</style>

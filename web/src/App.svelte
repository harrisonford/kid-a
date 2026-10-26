<script>
  import Message from './lib/Message.svelte'
  import Composer from './lib/Composer.svelte'

  // chats live only in this browser (localStorage), one per level
  const store = {
    get: (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d } catch { return d } },
    set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)) } catch {} },
  }

  let levels = $state([])
  let level = $state(store.get('kid-a:level', null))
  let history = $state([])
  let busy = $state(false)
  let scroller

  const card = $derived(levels.find((l) => l.id === level))

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
  <header>
    <b>kid-a</b>
    <select bind:value={level} disabled={!levels.length}>
      {#each levels as l (l.id)}<option value={l.id}>{l.id} · {l.name}</option>{/each}
    </select>
    <div class="card">{#if card}like a {card.human_age} · {card.summary}{:else}no level released yet{/if}</div>
    <button onclick={clear} title="clear this chat">clear</button>
  </header>

  <main bind:this={scroller}>
    <div class="log">
      {#if !history.length}
        <div class="empty">
          Talk to it like you would to a small child.<br />It only knows what its level has learned.
          {#if card}<div class="can">{card.can}</div>{/if}
        </div>
      {/if}
      {#each history as m, i (i)}<Message {m} />{/each}
      {#if busy}<div class="thinking">…</div>{/if}
    </div>
  </main>

  <Composer onsend={send} disabled={busy || !level} />
</div>

<style>
  .app { height: 100%; display: flex; flex-direction: column; }
  header { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-bottom: 1px solid var(--line); }
  b { letter-spacing: .5px; }
  .card { color: var(--dim); font-size: 13px; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  main { flex: 1; overflow-y: auto; }
  .log { max-width: 760px; margin: 0 auto; padding: 24px 16px 24px; }
  .empty { color: var(--dim); text-align: center; margin-top: 16vh; }
  .can { margin-top: 14px; font-size: 13px; }
  .thinking { color: var(--dim); font-size: 20px; }
</style>

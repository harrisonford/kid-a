<script>
  // text box with an optional picture (button, paste or drop); Enter sends, Shift+Enter is a new line
  let { onsend, disabled = false } = $props()
  let text = $state('')
  let image = $state(null)
  let file, box

  const ready = $derived(!disabled && (text.trim() || image))

  function read(f) {
    if (!f || !f.type.startsWith('image/')) return
    const r = new FileReader()
    r.onload = () => (image = r.result)
    r.readAsDataURL(f)
  }

  function submit(e) {
    e?.preventDefault()
    if (!ready) return
    onsend({ text: text.trim(), image })
    text = ''
    image = null
    if (file) file.value = ''
    grow()
  }

  function grow() {
    if (!box) return
    box.style.height = 'auto'
    box.style.height = box.scrollHeight + 'px'
  }
</script>

<svelte:window
  onpaste={(e) => read([...e.clipboardData.files].find((f) => f.type.startsWith('image/')))}
  ondragover={(e) => e.preventDefault()}
  ondrop={(e) => { e.preventDefault(); read([...e.dataTransfer.files][0]) }}
/>

<footer>
  <form onsubmit={submit}>
    <button type="button" class="round add" title="add a picture" onclick={() => file.click()}>＋</button>
    <input type="file" accept="image/*" hidden bind:this={file} onchange={(e) => read(e.target.files[0])} />
    {#if image}
      <div class="preview"><img src={image} alt="" /><button type="button" title="remove" onclick={() => (image = null)}>×</button></div>
    {/if}
    <textarea rows="1" placeholder="Say something, or show a picture…" bind:value={text} bind:this={box} oninput={grow}
      onkeydown={(e) => { if (e.key === 'Enter' && !e.shiftKey) submit(e) }}></textarea>
    <button class="round send" class:ready disabled={!ready} title="send">↑</button>
  </form>
</footer>

<style>
  footer { padding: 12px 16px 16px; flex: none; }
  form { max-width: 680px; margin: 0 auto; display: flex; gap: 6px; align-items: flex-end; background: var(--panel);
    border: 1px solid var(--line); border-radius: 24px; padding: 6px; }
  textarea { flex: 1; resize: none; border: 0; outline: 0; background: transparent; padding: 6px 4px; line-height: 24px; max-height: 160px; }
  textarea::placeholder { color: var(--faint); }
  .round { flex: none; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
  .add { color: var(--dim); font-size: 18px; }
  .add:hover { color: var(--text); background: var(--me); }
  .send { background: var(--line); color: var(--faint); font-size: 16px; }
  .send.ready { background: var(--text); color: var(--bg); font-weight: 600; }
  .preview { position: relative; flex: none; }
  .preview img { height: 36px; width: 36px; object-fit: cover; border-radius: 8px; display: block; }
  .preview button { position: absolute; top: -6px; right: -6px; width: 18px; height: 18px; border-radius: 50%; font-size: 11px; line-height: 18px;
    background: var(--me); border: 1px solid var(--line); }
</style>

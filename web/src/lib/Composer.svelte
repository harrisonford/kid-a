<script>
  // text box with an optional picture (button, paste or drop); Enter sends, Shift+Enter is a new line
  let { onsend, disabled = false } = $props()
  let text = $state('')
  let image = $state(null)
  let file, box

  function read(f) {
    if (!f || !f.type.startsWith('image/')) return
    const r = new FileReader()
    r.onload = () => (image = r.result)
    r.readAsDataURL(f)
  }

  function submit(e) {
    e?.preventDefault()
    if (disabled || (!text.trim() && !image)) return
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
    <button type="button" class="icon" title="add a picture" onclick={() => file.click()}>＋</button>
    <input type="file" accept="image/*" hidden bind:this={file} onchange={(e) => read(e.target.files[0])} />
    {#if image}
      <div class="preview"><img src={image} alt="" /><button type="button" title="remove" onclick={() => (image = null)}>×</button></div>
    {/if}
    <textarea rows="1" placeholder="Say something, or show a picture…" bind:value={text} bind:this={box} oninput={grow}
      onkeydown={(e) => { if (e.key === 'Enter' && !e.shiftKey) submit(e) }}></textarea>
    <button {disabled}>send</button>
  </form>
</footer>

<style>
  footer { padding: 12px 16px 16px; }
  form { max-width: 760px; margin: 0 auto; display: flex; gap: 8px; align-items: flex-end; background: var(--panel);
    border: 1px solid var(--line); border-radius: 16px; padding: 8px; }
  textarea { flex: 1; resize: none; border: 0; outline: 0; background: transparent; padding: 6px 4px; max-height: 160px; }
  .icon { padding: 6px 10px; }
  .preview { position: relative; }
  .preview img { height: 44px; border-radius: 8px; display: block; }
  .preview button { position: absolute; top: -8px; right: -8px; padding: 0; width: 20px; height: 20px; border-radius: 50%; font-size: 12px; line-height: 18px; }
</style>

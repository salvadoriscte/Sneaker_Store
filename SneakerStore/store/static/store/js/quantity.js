function aumentarQuantidade(event, id) {
  const quantidadeSpan = document.querySelector(`#quantidade-${id}`);
  let quantidade = parseInt(quantidadeSpan.innerText);
  quantidade++;
  atualizarQuantidade(quantidadeSpan, `quantidade-input-${id}`, quantidade);
}

function diminuirQuantidade(event, id) {
  const quantidadeSpan = document.querySelector(`#quantidade-${id}`);
  let quantidade = parseInt(quantidadeSpan.innerText);
  if (quantidade > 1) {
    quantidade--;
    atualizarQuantidade(quantidadeSpan, `quantidade-input-${id}`, quantidade);
  }
}

function atualizarQuantidade(quantidadeSpan, inputId, quantidade) {
  quantidadeSpan.innerText = quantidade;
const input = document.querySelector(`#${inputId}`);
  input.value = quantidade;
}
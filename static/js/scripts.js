const form = document.getElementById('buscarForm');
const input = document.getElementById('palabra_clave');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  
  fetch('/text_mining/minin_text.json', {
    method: 'PUT',
    body: JSON.stringify({
      palabra: input.value  
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      console.log('Palabra guardada correctamente');
    }
  })
  .catch(error => {
    console.error('Error guardando palabra:', error);
  });

});
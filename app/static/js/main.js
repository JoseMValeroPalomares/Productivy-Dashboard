document.addEventListener('DOMContentLoaded', () => {
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');

  togglePasswordButtons.forEach(button => {
    button.addEventListener('click', () => {
      const input = button.previousElementSibling; // el input de la contraseña
      const svg = button.querySelector('svg');

      if (input.type === 'password') {
        input.type = 'text';
        button.setAttribute('aria-label', 'Ocultar contraseña');

        // Cambiar icono a ojo abierto con línea ("ojo cerrado")
        svg.innerHTML = `
          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7zM12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z" />
          <path d="M12 9a3 3 0 0 1 3 3 2.996 2.996 0 0 1-2 2.82" />
        `;
      } else {
        input.type = 'password';
        button.setAttribute('aria-label', 'Mostrar contraseña');

        // Cambiar icono a ojo abierto normal ("ojo visible")
        svg.innerHTML = `
          <path d="M12 5c-7 0-9 7-9 7s2 7 9 7 9-7 9-7-2-7-9-7z"/>
          <circle cx="12" cy="12" r="2.5"/>
        `;
      }
    });
  });
});


document.addEventListener('DOMContentLoaded', function() {
  const asistente = document.getElementById('asistente-flotante');
  const btnAsistente = document.getElementById('boton-asistente');
  const cerrarAsistente = document.getElementById('cerrar-asistente');
  const ventanaAsistente = asistente.querySelector('.asistente-ventana');

  // Mostrar/ocultar ventana
  btnAsistente.addEventListener('click', () => {
    asistente.classList.toggle('abierto');
    asistente.classList.toggle('cerrado');
  });

  cerrarAsistente.addEventListener('click', () => {
    asistente.classList.remove('abierto');
    asistente.classList.add('cerrado');
  });

  // Opcional: cerrar al click fuera en móvil/escritorio si quieres
  ventanaAsistente.addEventListener('click', e => e.stopPropagation());
  document.body.addEventListener('click', function(e) {
    if (asistente.classList.contains('abierto') && !asistente.contains(e.target) && e.target !== btnAsistente) {
      asistente.classList.remove('abierto');
      asistente.classList.add('cerrado');
    }
  });

  // Si quieres inyectar avisos dinámicos desde JS (manual/test)
  // actualizaAvisos([
  //   { tipo:'tarea', titulo:'Tarea próxima', desc:'Entrega práctica IA — vence en 2h.' },
  //   { tipo:'meta', titulo:'Meta temporal', desc:'No has avanzado en “Leer capítulo 7”.' },
  //   { tipo:'evento', titulo:'Evento horario próximo', desc:'Clase de SO a las 16:00.' }
  // ]);
});

// Función auxiliar si tienes avisos calculados por backend o JS:
function actualizaAvisos(lista) {
  const contenido = document.getElementById('asistente-contenido');
  if (!contenido) return;
  if (!lista || lista.length === 0) {
    contenido.innerHTML = `<p>🎉 Nada pendiente importante por ahora.<br>¡Buen trabajo!</p>`;
    return;
  }
  contenido.innerHTML = lista.map(aviso => {
    let icono = 'fa-star';
    if (aviso.tipo === 'tarea') icono = 'fa-tasks';
    if (aviso.tipo === 'meta') icono = 'fa-flag-checkered';
    if (aviso.tipo === 'evento') icono = 'fa-calendar-day';
    return `<div class="asistente-aviso">
      <i class="fa ${icono}"></i>
      <div>
        <div class="aviso-titulo">${aviso.titulo}</div>
        <div class="aviso-descripcion">${aviso.desc}</div>
      </div>
    </div>`;
  }).join('');
}

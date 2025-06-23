// Funcionalidad mejorada para manejar comentarios
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formComentario")
  const comentariosContainer = document.getElementById("comentariosContainer")

  // Simular usuario logueado
  const usuarioLogueado = {
    nombre: "Usuario Actual",
    avatar: "./iconos/usuario.png",
  }

  // Manejar envío del formulario
  form.addEventListener("submit", (e) => {
    e.preventDefault()

    const comentarioTexto = document.getElementById("comentario").value.trim()

    if (comentarioTexto) {
      // Mostrar indicador de carga
      mostrarCargando()

      // Simular delay de envío
      setTimeout(() => {
        agregarComentario(usuarioLogueado.nombre, comentarioTexto)
        form.reset()
        ocultarCargando()
        mostrarMensaje("¡Comentario agregado exitosamente!", "success")
      }, 1000)
    } else {
      mostrarMensaje("Por favor escribe un comentario", "error")
    }
  })

  // Función para agregar un nuevo comentario
  function agregarComentario(nombre, texto) {
    const comentarioHTML = `
      <div class="comentario-item">
        <div class="comentario-header">
          <img src="${usuarioLogueado.avatar}" alt="Usuario" class="avatar">
          <div class="comentario-info">
            <h3 class="comentario-nombre">${nombre}</h3>
            <span class="comentario-fecha">Ahora</span>
          </div>
          <div class="comentario-rating">
            <img src="./iconos/saludo.png" alt="Like" class="like-icon" onclick="toggleLike(this)">
          </div>
        </div>
        <p class="comentario-texto">${texto}</p>
      </div>
    `

    // Insertar el nuevo comentario al principio de la lista
    comentariosContainer.insertAdjacentHTML("afterbegin", comentarioHTML)
  }

  // Función para mostrar indicador de carga
  function mostrarCargando() {
    const botonEnviar = document.querySelector(".boton-enviar")
    botonEnviar.disabled = true
    botonEnviar.innerHTML = `
      <div class="loading-spinner"></div>
      <span>Enviando...</span>
    `
  }

  // Función para ocultar indicador de carga
  function ocultarCargando() {
    const botonEnviar = document.querySelector(".boton-enviar")
    botonEnviar.disabled = false
    botonEnviar.innerHTML = `
      <img src="./iconos/ver.png" alt="Enviar" class="btn-icon">
      <span class="texto">Enviar</span>
    `
  }

  // Función para mostrar mensajes mejorada
  function mostrarMensaje(mensaje, tipo = "success") {
    const mensajeDiv = document.createElement("div")
    mensajeDiv.className = `mensaje-confirmacion ${tipo}`

    const icono = tipo === "success" ? "✓" : "⚠"
    mensajeDiv.innerHTML = `
      <span class="mensaje-icono">${icono}</span>
      <span class="mensaje-texto">${mensaje}</span>
    `

    const estilos =
      tipo === "success"
        ? "background: linear-gradient(145deg, #8a2be2, #6a1b9a);"
        : "background: linear-gradient(145deg, #e74c3c, #c0392b);"

    mensajeDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      ${estilos}
      color: white;
      padding: 15px 25px;
      border-radius: 15px;
      z-index: 2000;
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: bold;
      box-shadow: 0 8px 20px rgba(0,0,0,0.3);
      animation: slideIn 0.4s ease;
      backdrop-filter: blur(10px);
    `

    document.body.appendChild(mensajeDiv)

    // Remover el mensaje después de 4 segundos
    setTimeout(() => {
      mensajeDiv.style.animation = "slideOut 0.4s ease"
      setTimeout(() => {
        if (document.body.contains(mensajeDiv)) {
          document.body.removeChild(mensajeDiv)
        }
      }, 400)
    }, 4000)
  }

  // Función para manejar likes
  window.toggleLike = (elemento) => {
    elemento.style.transform = "scale(1.3)"
    elemento.style.filter =
      "brightness(0) saturate(100%) invert(27%) sepia(51%) saturate(2878%) hue-rotate(346deg) brightness(104%) contrast(97%)"

    setTimeout(() => {
      elemento.style.transform = "scale(1)"
    }, 200)

    mostrarMensaje("¡Te gusta este comentario!", "success")
  }

  // Agregar estilos CSS adicionales
  const style = document.createElement("style")
  style.textContent = `
    .loading-spinner {
      width: 20px;
      height: 20px;
      border: 2px solid #ffffff;
      border-top: 2px solid transparent;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .mensaje-icono {
      font-size: 1.2em;
      font-weight: bold;
    }
    
    .mensaje-texto {
      font-size: 1em;
    }
    
    .like-icon {
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .like-icon:hover {
      transform: scale(1.2);
      filter: brightness(0) saturate(100%) invert(27%) sepia(51%) saturate(2878%) hue-rotate(346deg) brightness(104%) contrast(97%);
    }
    
    /* Mejoras responsive para mensajes */
    @media (max-width: 480px) {
      .mensaje-confirmacion {
        top: 10px !important;
        right: 10px !important;
        left: 10px !important;
        padding: 12px 20px !important;
        font-size: 0.9em !important;
      }
    }
  `
  document.head.appendChild(style)

  // Inicializar likes existentes
  document.querySelectorAll(".like-icon").forEach((icon) => {
    icon.addEventListener("click", function () {
      window.toggleLike(this)
    })
  })
})


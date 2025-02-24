const maketodo = document.querySelector('#agregartarea');
const addtodo = document.querySelector('#add');
const contador = document.querySelector('#contador');

maketodo.addEventListener('input', e => {

    const cuenta = maketodo.value.split('').length + 1

    let count = 0
    for (let i = 0; i < cuenta; i++) {
         contador.innerHTML = `${count++}/150`

        }
         if (count >= 150) {
            contador.innerHTML = '150/150'
            addtodo.disabled = true
         } else if (count <= 1) {
            addtodo.disabled = true
         }
         else {
            addtodo.disabled = false
         }


})

// Al presioanr el botón que envie
// Se añade acopla un eventListener para capturar el evento de un clic en el boton "INGRESAR"
document.getElementById("ingresar").addEventListener('click', validate);

// Al hacer clic se ejecuta la funcion
function validate(ev) {

    //Variables que contienen los valores que se introdujeron en el formulario de la pagina
    var user = document.getElementById("username").value;
    var pass = document.getElementById("password").value;

    ev.preventDefault();   // Previene el envío del formulario y el paso a la siguiente página

    if(user=="" || pass=="") { // Se evalua si se dejo un campo vacio y se muestra un mensaje en caso sea así

        document.getElementById("msg").innerHTML="Por favor, rellene todos los campos"

    } else if(user=="admin" && pass=="1234") {             // Se evalúan los datos ingresados

        document.getElementById("login").submit();          // Si son correctos se envía el formulario y se avanza a la sgte pag
        } else {

            // Si los datos no concuerdan se muestra un mensaje
            document.getElementById("msg").innerHTML="Usuario o contraseña incorrectos. Por favor, vuelva a ingresar los datos"
        //alert ("Usuario o contraseña incorrecto");
    }
}

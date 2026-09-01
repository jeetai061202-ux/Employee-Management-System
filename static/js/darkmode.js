const darkBtn=document.getElementById("darkModeBtn");

darkBtn.addEventListener("click",function(){

    document.body.classList.toggle("dark-mode");

    localStorage.setItem(

        "theme",

        document.body.classList.contains("dark-mode")

    );

});

window.onload=function(){

    if(localStorage.getItem("theme")=="true"){

        document.body.classList.add("dark-mode");

    }

};
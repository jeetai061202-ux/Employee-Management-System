/* ===========================================
   Loader
=========================================== */

window.addEventListener("load",function(){

    const loader=document.getElementById("loader");

    loader.style.display="none";

});

/* ===========================================
   Scroll To Top
=========================================== */

const scrollBtn=document.getElementById("scrollTop");

window.onscroll=function(){

    if(document.documentElement.scrollTop>250){

        scrollBtn.style.display="block";

    }

    else{

        scrollBtn.style.display="none";

    }

};

scrollBtn.onclick=function(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

};

/* ===========================================
   Current Year
=========================================== */

document.getElementById("currentYear").innerHTML=new Date().getFullYear();
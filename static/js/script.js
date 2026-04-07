class Accordion {
  constructor(accordionListQuestions) {
    this.accordionListQuestions = document.querySelectorAll(accordionListQuestions);
    this.activeItemClass = "active";
  }

  toggleAccordion(item) {
    item.classList.toggle(this.activeItemClass);
    item.nextElementSibling.classList.toggle(this.activeItemClass);
  }

  addAccordionEvent() {
    this.accordionListQuestions.forEach((question) => {
      question.addEventListener("click", () => this.toggleAccordion(question));
    });
  }

  init() {
    if (this.accordionListQuestions.length) {
      this.addAccordionEvent();
    }
    return this;
  }
}

const accordion = new Accordion(".faq-question");
accordion.init();

// fetch("/registro_participantes")
// .then(res => res.text())
// .then(html => {
//     document.getElementById("areaAuth").innerHTML = html;
// });

// function mostrarLogin() {
//     document.getElementById("loginBox").style.display = "block";
//     document.getElementById("registroBox").style.display = "none";

//     document.getElementById("btnLogin").classList.add("active");
//     document.getElementById("btnRegistro").classList.remove("active");
// }

// function mostrarRegistro() {
//     document.getElementById("loginBox").style.display = "none";
//     document.getElementById("registroBox").style.display = "block";

//     document.getElementById("btnRegistro").classList.add("active");
//     document.getElementById("btnLogin").classList.remove("active");
// }
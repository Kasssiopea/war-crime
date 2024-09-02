
// Carousel Modal JS
var exampleModal = document.getElementById('exampleModal')
exampleModal.addEventListener('show.bs.modal', function (event) {
  var button = event.relatedTarget
  var recipient = button.getAttribute('data-bs-whatever')
  var modalBodyImg = exampleModal.querySelector('.modal-body img')

  modalBodyImg.src = recipient
});
// получаем ссылку на модальное окно
  var myModal = document.getElementById('exampleModal2');

  // добавляем обработчик события для каждой ссылки
  var links = document.querySelectorAll('[data-bs-toggle="modal"]');
  links.forEach(function(link) {
    link.addEventListener('click', function() {
      // получаем ссылку на изображение из атрибута data-bs-whatever у ссылки
      var imageSrc = this.getAttribute('data-bs-whatever');
      // устанавливаем полученную ссылку в атрибут src для тега img в модальном окне
      var modalImg = myModal.querySelector('.modal-body img');
      modalImg.setAttribute('src', imageSrc);
    });
  });
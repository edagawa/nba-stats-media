// js/main.js (修正版)

document.addEventListener('DOMContentLoaded', () => {

  // --- Hamburger Menu ---
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('.nav-menu');
  
  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('is-active');
      navMenu.classList.toggle('is-active');
    });
  }

  // --- Graph Modal ---
  const modal = document.querySelector('.modal');
  const modalContent = document.querySelector('.modal-content'); // '.modal-content-inner' から修正
  const modalClose = document.querySelector('.modal-close');
  const zoomBtns = document.querySelectorAll('.zoom-btn');

  if (modal && modalContent && modalClose) {
    zoomBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const graphContainer = btn.closest('.graph-container');
        const graphImage = graphContainer.querySelector('img');
        if (graphImage) {
          modalContent.innerHTML = ''; // Clear previous content
          const clonedGraph = graphImage.cloneNode(true);
          clonedGraph.style.width = '100%';
          clonedGraph.style.height = 'auto';
          modalContent.appendChild(clonedGraph);
          modal.classList.add('is-active');
        }
      });
    });

    const closeModal = () => {
        modal.classList.remove('is-active');
    };

    modalClose.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
  }
  
  // --- Accordion for Glossary page ---
  const accordionItems = document.querySelectorAll('.accordion-item');
  
  accordionItems.forEach(item => {
      const header = item.querySelector('.accordion-header');
      header.addEventListener('click', () => {
          // 他のアコーディオンを閉じる (任意)
          accordionItems.forEach(otherItem => {
              if (otherItem !== item) {
                  otherItem.classList.remove('active');
              }
          });
          // クリックしたアコーディオンを開閉
          item.classList.toggle('active');
      });
  });

});
const overlay = document.getElementById('overlay');
const main = document.getElementById('main-content');
const beginBtn = document.getElementById('begin');
const title = document.getElementById('title-text');

// Check if the intro has already been seen
const introSeen = sessionStorage.getItem('konnerverseIntro');

// Load visited projects from localStorage
const visitedProjects = JSON.parse(localStorage.getItem('visitedProjects') || '{}');

// Mark already visited projects
const projectListItems = document.querySelectorAll('#project-list li');
if (projectListItems.length) {
    projectListItems.forEach(li => {
        const key = li.dataset.key;
        if (visitedProjects[key]) {
            li.classList.add('visited');
        }
    });
}

// On each project page, mark it as visited
const currentProject = document.body.dataset.projectKey; // set this in <body data-project-key="{{ key }}">
if (currentProject) {
    visitedProjects[currentProject] = true;
    localStorage.setItem('visitedProjects', JSON.stringify(visitedProjects));
}

if (introSeen) {
  // Skip the intro entirely
  if (overlay) overlay.style.display = 'none';
  if (main) {
    main.classList.remove('hidden');
    main.classList.add('visible');
  }
} else {
  // Show typing animation and Begin button as normal
  if (title) {
    const fullText = title.textContent;
    title.textContent = '';
    let i = 0;
    const minSpeed = 60;
    const maxSpeed = 140;

    function type() {
      if (i < fullText.length) {
        title.textContent = fullText.slice(0, i + 1);
        i++;
        const delay = Math.random() * (maxSpeed - minSpeed) + minSpeed;
        setTimeout(type, delay);
      } else {
        title.classList.add('blink');
        beginBtn.classList.add('show');
      }
    }

    type();
  }

  if (beginBtn && overlay && main) {
    beginBtn.onclick = () => {
      overlay.classList.add('fade-out');
      setTimeout(() => {
        overlay.classList.add('hidden');
        main.classList.remove('hidden');
        main.classList.add('visible');

        // Remember that the intro has been seen
        sessionStorage.setItem('konnerverseIntro', 'true');
      }, 900);
    };
  }
}

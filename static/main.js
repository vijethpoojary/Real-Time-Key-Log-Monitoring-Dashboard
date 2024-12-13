window.onload = function () {
    document.getElementById('signup-modal').style.display = 'none';
    document.getElementById('registration-modal').style.display = 'none';
    document.getElementById('profile-modal').style.display = 'none';
  };

  // Functions to open and close modals
  function openModal() {
    document.getElementById('signup-modal').style.display = 'flex';
  }

  function closeModal() {
    document.getElementById('signup-modal').style.display = 'none';
  }

  function openRegistrationModal() {
    document.getElementById('registration-modal').style.display = 'flex';
  }

  function closeRegistrationModal() {
    document.getElementById('registration-modal').style.display = 'none';
  }
  function openProfileModal() {
    document.getElementById('profile-modal').style.display = 'flex';
  }

  function closeProfileModal() {
    document.getElementById('profile-modal').style.display = 'none';
  }


  // JavaScript function to filter PCs based on search input
  function filterPCs() {
    let input = document.getElementById("search-input").value.toUpperCase();
    let pcTiles = document.getElementsByClassName("pc-tile");

    for (let i = 0; i < pcTiles.length; i++) {
      let pcText = pcTiles[i].textContent || pcTiles[i].innerText;
      if (pcText.toUpperCase().indexOf(input) > -1) {
        pcTiles[i].style.display = ""; // Show matching PC
      } else {
        pcTiles[i].style.display = "none"; // Hide non-matching PCs
      }
    }
  }

  // Function to validate password confirmation
  function validateRegistration() {
    var password = document.getElementById("new-password").value;
    var confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
      alert("Passwords do not match. Please enter the correct password.");
      return false; // Prevent form submission
    }

    // If passwords match, allow form submission
    return true;
  }

   // Open popup function
   function openPopup() {
    document.getElementById('popup').style.display = 'flex';
  }

  // Close popup function
  function closePopup() {
    document.getElementById('popup').style.display = 'none';
  }
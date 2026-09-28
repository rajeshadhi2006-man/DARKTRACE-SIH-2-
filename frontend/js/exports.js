// Intelligence Dataset Export Controller

document.addEventListener('DOMContentLoaded', () => {
  const csvBtn = document.getElementById('btn-export-csv');
  const jsonBtn = document.getElementById('btn-export-json');

  if (csvBtn) {
    csvBtn.addEventListener('click', () => {
      window.location.href = '/api/export/csv';
    });
  }

  if (jsonBtn) {
    jsonBtn.addEventListener('click', () => {
      window.location.href = '/api/export/json';
    });
  }
});

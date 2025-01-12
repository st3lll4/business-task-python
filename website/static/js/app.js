const addShareholderBtn = document.getElementById("addShareholderBtn");
const shareholdersContainer = document.getElementById("shareholders-container");

addShareholderBtn.addEventListener("click", (event) => {
    event.preventDefault();
    addShareholder();
    // update
});

const totalCapitalInput = document.getElementById("total_capital");
let availableShares = parseInt(totalCapitalInput.value) || 0;

function updateShares() {
    //todo
}

totalCapitalInput.addEventListener("change", (event) => {
    availableShares = parseInt(event.target.value); // || 0 ??
    updateShares();
})

function createShareholderEntry() {
    const entryDiv = document.createElement("div");
    entryDiv.className = "row mb-3 justify-content-center shareholder-entry";

    const label = document.createElement("label");
    label.className = "col-sm-2 col-form-label";
    label.textContent = "Shareholder";

    const controlsDiv = document.createElement("div");
    controlsDiv.className = "col-sm-3";

    const select = document.createElement("select");
    select.className = "form-control mb-2";
    select.name = "shareholders[]";

    const originalSelect = document.querySelector('select[name="shareholders[]"]');
    if (originalSelect) {
        originalSelect.querySelectorAll('option').forEach(option => {
            const newOption = option.cloneNode(true);
            select.appendChild(newOption);
        });
    }

    const sharesInput = document.createElement("input");
    sharesInput.type = "number";
    sharesInput.className = "form-control";
    sharesInput.name = "shares[]";
    sharesInput.min = "1";
    sharesInput.placeholder = "Number of shares";

    const removeButton = document.createElement("button");
    removeButton.className = "btn btn-secondary ms-2 mt-2"; // Added margin classes
    removeButton.textContent = "Remove";
    removeButton.addEventListener("click", (event) => {
        event.preventDefault();
        entryDiv.remove();
        updateShares();
    });

    controlsDiv.appendChild(select);
    controlsDiv.appendChild(sharesInput);
    controlsDiv.appendChild(removeButton);
    entryDiv.appendChild(label);
    entryDiv.appendChild(controlsDiv);

    return entryDiv;
}

function addShareholder() {
    const newEntry = createShareholderEntry();
    shareholdersContainer.appendChild(newEntry);
}
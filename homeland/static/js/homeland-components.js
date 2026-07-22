(function () {

function progressBar(percent){

    percent = Number(percent) || 0;

    const track=document.createElement("div");
    track.className="progress-track";

    const bar=document.createElement("div");
    bar.className="progress-bar";

    bar.style.width=percent+"%";

    if(percent>=90)
        bar.style.background="#d9534f";
    else if(percent>=75)
        bar.style.background="#f0ad4e";
    else
        bar.style.background="#5cb85c";

    track.appendChild(bar);

    return track;

}

function progressMetric(metricId,label,value,percent){

    const metric=document.getElementById(metricId);

    if(!metric)
        return;

    metric.innerHTML="";

    const title=document.createElement("span");
    title.textContent=label;

    const strong=document.createElement("strong");
    strong.textContent=value;

    metric.appendChild(title);
    metric.appendChild(strong);
    metric.appendChild(progressBar(percent));

}

function storageCard(drive){

    const card=document.createElement("div");
    card.className="metric";

    const title=document.createElement("span");
    title.textContent=drive.letter;

    const value=document.createElement("strong");
    value.textContent=drive.display;

    const small=document.createElement("small");
    small.textContent=drive.used_percent+"% used";

    card.appendChild(title);
    card.appendChild(value);
    card.appendChild(progressBar(drive.used_percent));
    card.appendChild(small);

    return card;

}

function renderStorageGrid(containerId,drives){

    const container=document.getElementById(containerId);

    if(!container)
        return;

    container.innerHTML="";

    drives.forEach(function(drive){

        container.appendChild(storageCard(drive));

    });

}

window.HomelandComponents={
    progressBar,
    progressMetric,
    storageCard,
    renderStorageGrid
};

})();

var CURRENT_MAIN = null
var PROTECTION_STATUS = false
var AGENT_LOADED = false
var MAIN_INTERVALS = []
var VERSION = "0.0"

moveTo("home")

function moveTo(id) {
    if (CURRENT_MAIN == id)
        return
    MAIN_INTERVALS.forEach((id) => {
        clearInterval(id)
    })
    CURRENT_MAIN = id
    if (!document.getElementById("main-content").classList.contains("hide")) {
        document.getElementById("main-content").classList.add("fade_out")
        setTimeout(async () => {
            var main_content = await eel.get_main_content(id)()
            document.getElementById("main-content").classList.remove("fade_out")
            document.getElementById("main-content").innerHTML = main_content
            document.getElementById("main-content").classList.add("fade_in")
            setTimeout(() => {
                document.getElementById("main-content").classList.remove("fade_in")
            }, 400)
        }, 400)
    } else {
        setTimeout(async () => {
            var main_content = await eel.get_main_content(id)()
            document.getElementById("main-content").innerHTML = main_content
            document.getElementById("loader-wrapper").classList.add("fade_out_no_transform")
            setTimeout(() => {
                document.getElementById("loader-wrapper").remove()
                document.getElementById("main-content").classList.remove("hide")
                document.getElementById("main-content").classList.add("fade_in")
                setTimeout(() => {
                    document.getElementById("main-content").classList.remove("fade_in")
                }, 400)
            }, 400)
        }, 100)
    }
}

async function toggleProtection() {
    PROTECTION_STATUS = !PROTECTION_STATUS
    eel.toggle_protection(PROTECTION_STATUS)
    on_off_button = document.getElementById("on-off-button")
    if (PROTECTION_STATUS) {
        on_off_button.classList.remove("off")
        on_off_button.classList.remove("on")
        on_off_button.classList.add("load")
        MAIN_INTERVALS.push(setInterval(async () => {
            AGENT_LOADED = await eel.get_agent_status()()
            console.log(AGENT_LOADED)
            if (AGENT_LOADED) {
                on_off_button.classList.remove("load")
                on_off_button.classList.add("on")
                on_off_button.getElementsByTagName("img")[0].src = "./images/power.png"
                on_off_button.classList.remove("spin")
            }
        }, 1000))
    } else {
        on_off_button.classList.add("off")
        on_off_button.classList.remove("load")
        on_off_button.classList.remove("on")
    }
    if (on_off_button.classList.contains("load")) {
        on_off_button.getElementsByTagName("img")[0].src = "./images/load.png"
        on_off_button.classList.add("spin")
    } else {
        on_off_button.getElementsByTagName("img")[0].src = "./images/power.png"
        on_off_button.classList.remove("spin")
    }
}

function activeLoaded() {
    on_off_button = document.getElementById("on-off-button")
    if (PROTECTION_STATUS && AGENT_LOADED) {
        on_off_button.classList.add("on")
    } else if(PROTECTION_STATUS && !AGENT_LOADED) {
        on_off_button.classList.add("load")
    } else {
        on_off_button.classList.add("off")
    }
    if (on_off_button.classList.contains("load")) {
        on_off_button.getElementsByTagName("img")[0].src = "./images/load.png"
        on_off_button.classList.add("spin")
    } else {
        on_off_button.getElementsByTagName("img")[0].src = "./images/power.png"
        on_off_button.classList.remove("spin")
    }
}

function settingsLoaded() {
    (async () => {
        settings = await eel.get_settings()()
        Object.keys(settings).forEach((key) => {
            input = document.getElementById(key)
            if (input.tagName.toLowerCase() == "ul") {
                settings[key].map((dir) => {
                    input.innerHTML += `<li id="process-scan-filter-folder-${dir}">${dir}<button onclick="removeFilterFolder('${dir}')">Remove</button></li>`
                })
            }
            if (input.type == "checkbox") {
                input.checked = settings[key]
            }
        })
    })()
}

async function updateFilterFolders() {
    var dir = await eel.update_filter_folders()();
    if (dir !== "") {
        document.getElementById("process-scan-filter-folders").innerHTML += `<li id="process-scan-filter-folder-${dir}">${dir}<button onclick="removeFilterFolder('${dir}')">Remove</button></li>`
    }
}

function removeFilterFolder(dir) {
    eel.remove_filter_folders(dir)
    document.getElementById(`process-scan-filter-folder-${dir}`).remove()
}

function settingUpdate(name, value) {
    eel.update_settings(name, value)
}

function getUnprotected() {
    (async () => {
        document.getElementById("content-main-button").innerText = "..."
        unprotected = await eel.get_unprotected()()
        verif_result = document.getElementById("verif-result")
        verif_result.innerHTML = ""
        for(var i = 0; i < unprotected.length; i++){
            info = unprotected[i]
            verif_result.innerHTML += `<span class="info"><span class="status not-securised">Not securised</span>${info.split(".")[0]}<span class="blur">${info.split(".").splice(1).join(".")}</span></span>`
        }
        document.getElementById("content-main-button").innerText = "Check infos"
    })()
}

function statsLoaded() {
    (async () => {
        stats = await eel.get_stats()()
        Object.keys(stats).forEach((key) => {
            input = document.getElementById(key)
            input.textContent = stats[key]
        })
    })()
}

(async () => {
    AGENT_LOADED = await eel.get_agent_status()()
    PROTECTION_STATUS = await eel.get_info("protection_status")()
    VERSION = await eel.get_version()()
    document.getElementById("version").textContent = "v" + VERSION
})()
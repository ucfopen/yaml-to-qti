function hide(id) {
	const target = document.getElementById(id)
	if ( ! target.classList.contains("hidden")) {
		target.classList.add("hidden")
	}
}
function show(id) {
	const target = document.getElementById(id)
	if ( target.classList.contains("hidden")) {
		target.classList.remove("hidden")
	}
}

function backToDefault() {
	hide("exposition-media")
	hide("media-input")
	hide("upload-button")
}

// parse the uploaded YAML for certain important flags
// if we find any that require additional input, handle them
function checkFileContents(e) {
	let yamlObject = jsyaml.load(e.target.result)
	
	let hasMedia = false
	for (const i in yamlObject.questions) {
		const q = yamlObject.questions[i]
		// this is kind of extraneous
		// as it is, all of the relevant properties for a
		//  question are two layers deep rather than one,
		//  because the first child of each question object
		//  is a sub-object keyed on that question's type
		// rather than having question type as a sub-object,
		//  it should just be a property along with all of
		//  the other question properties
		// if that ever happens, revisit this
		const questionType = Object.keys(q)
		const qProps = q[questionType]

		if (qProps.figure) {
			hasMedia = true
			break
		}
	}
	if (hasMedia) {
		show("exposition-media")
		show("media-input")
	} else {
		show("upload-button")
	}
}

function handleError(error) {
	document.getElementById("error-message").textContent = error
	show("error-background")
}
function clearError() {
	hide("error-background")
	document.getElementById("error-message").textContent = null
}

window.onload = function() {
	let uploadedFile = null

	document.getElementById("file-in").value = null
	document.getElementById("file-in").addEventListener("change", e => {
		uploadedFile = null
		backToDefault()

		uploadedFile = e.target.files[0] ?? null

		// don't bother trying to deal with zip files
		// may be safer to check extensions here
		if (uploadedFile.type == "application/zip" ||
		uploadedFile.type == "application/x-zip-compressed") {
			show("upload-button")
			return
		}

		// otherwise it's a YAML file, check it for media
		let reader = new FileReader()
		reader.onload = e => {
			return checkFileContents(e)
		}
		reader.readAsText(e.target.files[0])
	}, false)

	document.getElementById("media-in").value = null
	document.getElementById("media-in").addEventListener("change", () => {
		if (uploadedFile) {
			show("upload-button")
		}
	})

	document.getElementById("error-close").addEventListener("click", clearError)

	let downloadId = null

	const uploadForm = document.getElementById("upload-form")
	uploadForm.addEventListener("submit", e => {
		e.preventDefault()
		const uploadBody = new FormData()
		
		// have to get the uploaded file(s) by hand
		const mainFile = document.getElementById("file-in")?.files[0] ?? null
		const mediaFile = document.getElementById("media-in")?.files[0] ?? null

		uploadBody.append("shuffle", document.getElementById("shuffle").checked)

		// it shouldn't be possible to get here in this case, but
		// TODO: error if we don't at least have a mainFile
		// maybe also if the media file uploader is visible but we don't have a mediaFile
		if (mainFile) uploadBody.append("main", mainFile)
		if (mediaFile) uploadBody.append("media", mediaFile)

		fetch(uploadForm.action, {
			method: "POST",
			body: uploadBody
		})
		.then(response => {
			// any issues that happen on the back end will be returned with 500 errors
			// since they are sent as json we still have to process the response first
			if ( ! response.ok) {
				throw response.json()
			}
			return response.json()
		})
		.then(response => {
			downloadId = response.id ?? null

			// simulate a download link click so we don't accidentally redirect to nowhere
			const downloadLink = document.createElement("a")
			downloadLink.href = `${APP_ROOT}/download/${downloadId}`
			downloadLink.download = "qti_import.zip"
			downloadLink.target = "_blank"
			document.body.appendChild(downloadLink)

			downloadLink.click()
			document.body.removeChild(downloadLink)
		})
		.catch(e => {
			e.then(error => {
				handleError(error.message)
			})
		})
	})
}
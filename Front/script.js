class JSONDisplay {
    constructor(url, targetElementId) {
        this.url = url;
        this.targetElementId = targetElementId;
    }

    async fetchData() {
        try {
            const response = await fetch(this.url);
            const jsonData = await response.json();
            return jsonData;
        } catch (error) {
            console.error('Error fetching JSON data:', error);
            return null;
        }
    }

    async displayData() {
        const jsonData = await this.fetchData();
        if (jsonData) {
            const targetElement = document.getElementById(this.targetElementId);
            if (targetElement) {
                targetElement.textContent = JSON.stringify(jsonData, null, 2);
            } else {
                console.error(`Target element with ID '${this.targetElementId}' not found.`);
            }
        }
    }z
}

// Usage: Create an instance of the JSONDisplay class and display the JSON data
const jsonDisplay = new JSONDisplay('http://127.0.0.1:5000', 'json-output');
jsonDisplay.displayData();

# Comprehensive Guide: AnythingLLM Data Export & Cursor Integration

## Part 1: Exporting the Vector Database from AnythingLLM

### Can I export the database?
**Yes, but it requires conversion.** AnythingLLM typically uses **LanceDB** (local files) by default. There is no "Export" button in the UI, and you cannot simply upload the raw database files to tools like ChatGPT or Claude because those tools require text, not binary vector data.

To use your data elsewhere, you must extract the text payload from the database and save it as a generic format like CSV or JSON.

### Location of Default Database Files
If you haven't changed the settings, your data is located here:
* **Windows:** `C:\Users\%USERNAME%\AppData\Roaming\anythingllm-desktop\storage\lancedb`
* **Mac:** `/Users/<username>/Library/Application Support/anythingllm-desktop/storage/lancedb`
* **Linux:** `/home/<username>/.config/anythingllm-desktop/storage/lancedb`
* **Docker:** In the volume path mounted to `/app/server/storage`

## Part 2: Integrating AnythingLLM with Cursor AI

You can connect your knowledge base to the Cursor IDE using the **Model Context Protocol (MCP)**.

### Method A: The MCP Bridge (Recommended for Global Knowledge)
This connects Cursor directly to your running AnythingLLM instance.

1.  **AnythingLLM:** Go to `Settings > Features > MCP Server` and enable it. Copy the command provided.
2.  **Cursor:** Go to `Settings > Features > MCP`. Click `+ Add New MCP Server`.
    * **Name:** `AnythingLLM`
    * **Type:** `command`
    * **Command:** Paste the command from AnythingLLM.
3.  **Usage:** In Cursor Composer (`Cmd+I` or `Ctrl+I`), type a prompt like "Check AnythingLLM for auth patterns."

### Method B: Native Cursor RAG (Recommended for Project-Specific Docs)
1.  **Action:** Export your text from AnythingLLM (using the script above) or take the original PDF.
2.  **Setup:** Drop the file into your Cursor project folder (e.g., inside a `docs/` folder).
3.  **Usage:** Reference it in chat using `@Docs` or `@Files`.

### Comparison: Which approach is better?

| Feature | Method A: MCP (AnythingLLM) | Method B: Native (Cursor) |
| :--- | :--- | :--- |
| **Scope** | **Global:** Good for company wikis, language manuals, standard libraries. | **Local:** Good for specific requirements of the current project. |
| **Setup** | Requires running the AnythingLLM app in background. | Zero setup; just drag and drop files. |
| **Parsing Quality** | **High:** AnythingLLM handles tables/OCR better. | **Standard:** Cursor is optimized for code, not complex PDF layouts. |
| **Privacy** | Vectors stay local on your machine. | Depends on if you use "Codebase Indexing" (cloud). |

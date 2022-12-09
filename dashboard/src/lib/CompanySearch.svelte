<script>
  import { elasticsearch_url_format_str } from "../constants";

  let search_term;

  export let found_companies = [];

  async function submit(evt) {
    evt.preventDefault();

    const url = elasticsearch_url_format_str.replace("{index}", "companies");
    const query = {
      query: {
        multi_match: {
          query: search_term,
          fields: ["name", "std_name"],
        },
      },
    };

    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(query),
    });
    let json = await response.json();
    console.log(json);
    if ("error" in json) {
      console.error(json["error"]);
    } else {
      let hits = json["hits"];
      found_companies = hits["hits"].map((document) => ({
        data: document["_source"],
        score: document["_score"],
      }));
    }
  }
</script>

<section>
  <form id="company-name-search" on:submit={submit}>
    <label for="site-search">
      <p>Search Company Dataset by Company Name:</p>
      <input
        type="search"
        id="site-search"
        placeholder="Company Name"
        required
        minlength="3"
        bind:value={search_term}
      />
      <button type="submit">Search</button>
    </label>
  </form>
</section>

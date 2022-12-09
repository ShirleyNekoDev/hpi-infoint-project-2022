<script>

  export let companies = [];

  let selected_company = "";

  function address2string(address_obj) {
    if(address_obj)
      return `${address_obj["street"]}, ${address_obj["zipcode"]} ${address_obj["city"]}`;
    else
      return "";
  }

  function selectCompany(company) {
    selected_company = company["data"]["id"];
  }
</script>

<ol>
  {#if companies && companies.length}
    <h1>Selected company id: {selected_company}</h1>
  {/if}
  {#each companies as company}
    <li
      class:selected={company["data"]["id"] == selected_company}
      on:click={() => selectCompany(company)}>
      <h2>{company["data"]["name"]}</h2>
      <p>{address2string(company["data"]["address"])}</p>
      <p>{company["data"]["id"]}</p>
    </li>
  {/each}
</ol>

<style>
  li.selected {
    background-color: gray;
  }
</style>

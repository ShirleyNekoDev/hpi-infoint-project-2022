<script>
  import CompanyList from "./lib/CompanyList.svelte";
import SearchBar from "./lib/CompanySearch.svelte";

  let found_companies = [];
</script>

<section>
  <aside>
    <SearchBar bind:found_companies />
    <CompanyList companies={found_companies} />
  </aside>
  <main />
</section>

<style>
  aside,
  main {
    border: thin solid white;
  }
</style>

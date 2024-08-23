<template>
  <div id="nav-container">
    <div id="nav">
      <h1>Tutortime</h1>
      <ul>
        <li>
          <RouterLink to="/">
            <h3>Take lessons</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ path: '/user/services', query: { status: 'active' } }">
            <h3>Give lessons</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/">
            <h3>How it works</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/">
            <h3>Learning hub</h3>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/user/login">
            <h3>Login</h3>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
#nav-container {
  display: flex;
  justify-content: center;
  background-color: var(--base1);
  height: 70px;
  width: 100%;

  #nav {
    display: flex;
    flex-direction: row;
    text-align: center;
    align-items: center;
    max-width: 1440px;
    width: 100%;

    h1,
    h3 {
      padding: 25px;
      margin: 0px;
    }

    i {
      padding: 4px;
    }

    ul {
      margin: 0px;
      padding: 0px;
      display: flex;
      list-style: none;
      align-items: center;
    }

    a {
      color: var(--text0);
    }

    .user-buttons {
      justify-content: flex-end;
      margin-left: auto;
      padding: 10px;
      cursor: pointer;
    }
  }

  .new-messages {
    color: var(--green0);
  }
}
</style>

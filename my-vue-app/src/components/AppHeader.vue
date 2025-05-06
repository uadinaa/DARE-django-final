<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4 fixed-top">
        <div class="container-fluid">
            <router-link class="navbar-brand" :to="{ name: 'home' }">MyApp</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav mx-auto">
                    <li class="nav-item">
                        <router-link class="nav-link" :to="{ name: 'home' }" active-class="active">Лента</router-link>
                    </li>
                    <li class="nav-item"><router-link class="nav-link" to="/somepage">Page in future</router-link></li>
                </ul>
                <ul class="navbar-nav">
                    <template v-if="!isLoggedIn">
                        <li class="nav-item">
                            <router-link class="nav-link" :to="{ name: 'login' }"
                                active-class="active">Вход</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" :to="{ name: 'register' }"
                                active-class="active">Регистрация</router-link>
                        </li>
                    </template>
                    <li class="nav-item" v-if="isLoggedIn">
                        <button class="btn btn-outline-danger btn-sm" @click="performLogout">Выход</button>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script setup>
// --- Скрипт остается тот же (с isLoggedIn и performLogout) ---
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const isLoggedIn = computed(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
        return !!localStorage.getItem('accessToken');
    }
    return false;
});

const performLogout = () => {
    if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    }
    router.push({ name: 'login' }).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
            console.error('Router push error:', err);
        }
    });
};
</script>

<style scoped>
/* --- Стили остаются те же --- */
.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
}

.nav-link.active {
    font-weight: bold;
    color: #ffffff !important;
}

.navbar-nav .nav-item {
    display: flex;
    align-items: center;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

.btn-sm {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}
</style>
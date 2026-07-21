import { Component, inject, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { HeaderComponent } from '../header/header.component';
import { AuthStore } from '../../domains/auth/store/auth.store';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, HeaderComponent],
  template: `
    <div class="flex h-screen w-full bg-bg overflow-hidden">
      <app-sidebar />
      
      <div class="flex-1 flex flex-col ml-64 overflow-hidden relative z-10">
        <app-header />
        
        <main class="flex-1 overflow-y-auto overflow-x-hidden relative">
          <!-- Page content goes here -->
          <div class="container mx-auto max-w-7xl">
            <router-outlet />
          </div>
        </main>
      </div>
    </div>
  `
})
export class MainLayoutComponent implements OnInit {
  private readonly authStore = inject(AuthStore);

  ngOnInit() {
    // Ensure user state is loaded from local storage on layout init
    if (!this.authStore.user()) {
      this.authStore.loadUserFromStorage();
    }
  }
}

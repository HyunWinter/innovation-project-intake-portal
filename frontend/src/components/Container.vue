<template>
  <main class="flex flex-1 justify-center w-full min-h-[calc(100vh-4rem)]">
    <div
      class="mx-auto flex w-full max-w-350 flex-col border-dashed min-[1400px]:border-x min-[1800px]:max-w-384"
    >
      <div class="flex w-full flex-1 flex-col px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        <slot></slot>
      </div>
    </div>
  </main>
</template>

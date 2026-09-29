---
name: emacs
description: Emacs configuration — the krons package stack for completion, navigation, git, and AI. NOT for host or service configuration (use ops), NOT for writing elisp application code.
when_to_use: set up Emacs, configure Emacs, Emacs packages, init.el, elisp config, use-package, MELPA, completion stack, vertico, orderless, marginalia, corfu, consult, avy, magit, gptel, codeium, aidermacs, vterm, AI in Emacs, Claude Code in Emacs, Emacs keybindings
---

# Emacs Setup

Ask the user which sections they want before generating any elisp.
Default: all. Each section is independent.

## Completion

Packages: vertico, orderless, marginalia, corfu, consult.

```elisp
(use-package vertico :ensure t :init (vertico-mode))
(use-package orderless :ensure t
  :custom (completion-styles '(orderless basic)))
(use-package marginalia :ensure t :init (marginalia-mode))
(use-package corfu :ensure t :init (global-corfu-mode))
(use-package consult :ensure t
  :bind (("C-s" . consult-line)
         ("C-x b" . consult-buffer)))
```

## Navigation

```elisp
(use-package avy :ensure t
  :bind ("C-;" . avy-goto-char))
```

## Git

```elisp
(use-package magit :ensure t
  :bind ("C-x g" . magit-status))
```

## AI

Three layers: autocomplete (codeium), chat (gptel), agentic (Claude Code / aidermacs).

```elisp
;; Autocomplete — free, 70+ languages
(use-package codeium :ensure t
  :init (add-to-list 'completion-at-point-functions #'codeium-completion-at-point))

;; Chat — multi-provider
(use-package gptel :ensure t
  :bind ("C-c a g" . gptel)
  :config
  (setq gptel-model 'claude-sonnet-5-5
        gptel-backend (gptel-make-anthropic "Anthropic"
                        :stream t
                        :key (lambda ()
                               (or (getenv "ANTHROPIC_API_KEY")
                                   (user-error "ANTHROPIC_API_KEY is not set"))))))

;; Agentic — Claude Code in vterm at project root
(defun krons-claude ()
  (interactive)
  (let ((root (or (and (project-current) (project-root (project-current)))
                  default-directory)))
    (vterm)
    (vterm-send-string (format "cd %s && claude\n" root))))
(global-set-key (kbd "C-c a c") #'krons-claude)

;; Inline pair programming via Aider (optional)
(use-package aidermacs :ensure t
  :config (setq aidermacs-backend 'vterm))
```

## Notes

- Requires `use-package` (built-in since Emacs 29; `M-x package-install use-package` on older)
- codeium.el is on MELPA — ALWAYS add `(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/") t)` to init.el first
- ALWAYS export `ANTHROPIC_API_KEY` before starting Emacs — gptel errors loudly without it
- vterm requires a C compiler; fallback: replace `(vterm)` with `(ansi-term "/bin/bash")`
- Claude Code is terminal-native — no Emacs-specific config needed beyond the keybind

package main

import (
	"context"
	"fmt"
	"log"

	"github.com/google/go-github/v39/github"
	"golang.org/x/oauth2"
)

const (
	githubToken        = "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"
	firebaseConfigPath = "./credentials.json"
)

func main() {
	ctx := context.Background()

	// Connect to GitHub
	ts := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: githubToken},
	)
	tc := oauth2.NewClient(ctx, ts)
	client := github.NewClient(tc)

	// Replace with your GitHub repository information
	owner := "machakann"
	repo := "vim-sandwich"

	// Get all issues from the GitHub repository
	issues, _, err := client.Issues.List(ctx, true, &github.IssueListOptions{
		Filter: "all",
	})

	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Found %d issues in %s/%s\n", len(issues), owner, repo)

	// print issues
	for _, issue := range issues {
		fmt.Printf("%d %s\n", issue.GetNumber(), issue.GetTitle())
	}

}
